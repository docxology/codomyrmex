import pytest
import sys
import os
import torch

# Resolve path to submodule regardless of working directory
_GHOST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../agents/ghost_architecture')
)
sys.path.insert(0, _GHOST_PATH)

try:
    from config import GhostConfig, TrainingConfig
    from model import GhostTransformer
    from router import Router, NeuromodulationState
except ImportError as exc:
    pytest.skip(
        f"Ghost architecture submodule not found or missing PyTorch: {exc}",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def small_config() -> GhostConfig:
    """Minimal-dimension GhostConfig that runs on CPU in milliseconds."""
    cfg = GhostConfig(num_modules=10, vocab_size=11, num_classes=11, operations=['add'])
    cfg.module.hidden_dim = 16
    cfg.module.num_heads = 2
    cfg.router.signature_dim = 8
    return cfg


@pytest.fixture()
def model(small_config) -> GhostTransformer:
    """Instantiated GhostTransformer in eval mode."""
    m = GhostTransformer(small_config)
    m.eval()
    return m


@pytest.fixture()
def input_batch() -> torch.Tensor:
    """(4, 2) random token indices in vocab_size=11."""
    return torch.randint(0, 11, (4, 2))


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------

def test_ghost_config_defaults():
    """GhostConfig default values match documented hyperparameters."""
    config = GhostConfig()
    assert config.vocab_size == 97
    assert config.num_classes == 97
    assert config.num_modules == 40
    assert config.operations == ['add']
    assert config.router.top_k == 6


def test_ghost_config_prime_shorthand():
    """Setting prime= should set both vocab_size and num_classes."""
    cfg = GhostConfig(prime=13, num_modules=10, operations=['add'])
    assert cfg.vocab_size == 13
    assert cfg.num_classes == 13


def test_ghost_config_validation_top_k():
    """Config should reject top_k > num_modules."""
    with pytest.raises(AssertionError):
        GhostConfig(num_modules=3, operations=['add'])  # top_k=6 > 3 → error


# ---------------------------------------------------------------------------
# Instantiation tests
# ---------------------------------------------------------------------------

def test_ghost_transformer_instantiation(small_config):
    """Per-task components exist for every declared operation."""
    cfg = small_config
    cfg.operations = ['add', 'mul']
    cfg = GhostConfig(
        num_modules=10, vocab_size=11, num_classes=11, operations=['add', 'mul']
    )
    cfg.module.hidden_dim = 16
    cfg.router.signature_dim = 8
    m = GhostTransformer(cfg)
    for op in ['add', 'mul']:
        assert op in m.pos_embs, f"pos_embs missing '{op}'"
        assert op in m.heads, f"heads missing '{op}'"
        assert op in m.sig_projs, f"sig_projs missing '{op}'"
        assert op in m.route_projs, f"route_projs missing '{op}'"
        assert op in m.fusion_projs, f"fusion_projs missing '{op}'"


def test_ghost_transformer_parameter_count(model, small_config):
    """Model has a non-trivial (>0) number of learnable parameters."""
    total = sum(p.numel() for p in model.parameters())
    assert total > 0


# ---------------------------------------------------------------------------
# Forward-pass tests
# ---------------------------------------------------------------------------

def test_ghost_forward_pass(model, input_batch):
    """Real forward pass produces logits with correct shape."""
    with torch.no_grad():
        logits = model(input_batch, task='add')
    assert logits.shape == (4, 11), f"Expected (4, 11), got {logits.shape}"


def test_ghost_forward_pass_no_nan(model, input_batch):
    """Logits must be finite — no NaN or Inf from the model."""
    with torch.no_grad():
        logits = model(input_batch, task='add')
    assert torch.isfinite(logits).all(), "Logits contain NaN or Inf"


def test_ghost_routing_info(model, input_batch):
    """When return_routing=True the model returns a complete info dict."""
    with torch.no_grad():
        logits, info = model(input_batch, return_routing=True, task='add')
    assert logits.shape == (4, 11)
    for key in ('routing_weights', 'active_mask', 'signature', 'routing_entropy', 'task'):
        assert key in info, f"routing_info missing key '{key}'"
    assert info['task'] == 'add'
    # routing_weights rows should sum to 1 (softmax)
    row_sums = info['routing_weights'].sum(dim=-1)
    assert torch.allclose(row_sums, torch.ones_like(row_sums), atol=1e-5)


def test_ghost_default_task_is_first_operation(model, input_batch):
    """Omitting task= should default to the first registered operation."""
    with torch.no_grad():
        logits_default = model(input_batch)
        logits_explicit = model(input_batch, task='add')
    assert torch.allclose(logits_default, logits_explicit)


# ---------------------------------------------------------------------------
# Dynamic head tests
# ---------------------------------------------------------------------------

def test_ghost_add_head(model, input_batch):
    """add_head() creates a new per-task isolation bundle."""
    model.add_head('sub')
    assert 'sub' in model.pos_embs
    assert 'sub' in model.heads
    with torch.no_grad():
        logits = model(input_batch, task='sub')
    assert logits.shape == (4, 11)


def test_ghost_add_head_idempotent(model):
    """Calling add_head twice with the same task name should not raise."""
    model.add_head('sub')
    model.add_head('sub')  # must be idempotent
    assert 'sub' in model.heads


# ---------------------------------------------------------------------------
# Freezing / crystallization tests
# ---------------------------------------------------------------------------

def test_ghost_freeze_task_head(model):
    """After freeze_task_head, positional emb and head params require no grad."""
    model.train()  # enable grad tracking
    model.freeze_task_head('add')
    for param in model.pos_embs['add'].parameters():
        assert not param.requires_grad, "pos_embs['add'] should be frozen"
    for param in model.heads['add'].parameters():
        assert not param.requires_grad, "heads['add'] should be frozen"


def test_ghost_freeze_task_head_invalid_raises(model):
    """freeze_task_head on an unknown task should raise ValueError."""
    with pytest.raises(ValueError):
        model.freeze_task_head('unknown_task')


def test_ghost_freeze_crystallized_modules(model):
    """After freezing modules the bank weights require no grad."""
    model.train()
    model.freeze_crystallized_modules([0, 1])
    for idx in [0, 1]:
        for param in model.bank.module_list[idx].parameters():
            assert not param.requires_grad, f"Module {idx} should be frozen"


# ---------------------------------------------------------------------------
# Continual-learning regression test
# ---------------------------------------------------------------------------

def test_ghost_continuous_learning_no_shape_regression(small_config):
    """Two tasks co-exist: forward for each task produces correct logits."""
    cfg = GhostConfig(
        num_modules=10, vocab_size=11, num_classes=11, operations=['add']
    )
    cfg.module.hidden_dim = 16
    cfg.router.signature_dim = 8
    m = GhostTransformer(cfg)
    m.add_head('mul')
    m.eval()

    x = torch.randint(0, 11, (3, 2))
    with torch.no_grad():
        logits_add = m(x, task='add')
        logits_mul = m(x, task='mul')
    assert logits_add.shape == (3, 11)
    assert logits_mul.shape == (3, 11)


# ---------------------------------------------------------------------------
# Neuromodulation tests
# ---------------------------------------------------------------------------

def test_neuromodulation_state_dopamine_update(small_config):
    """NeuromodulationState tracks dopamine from prediction error."""
    cfg = small_config.neuromodulation
    cfg.enabled = True
    state = NeuromodulationState(cfg, num_modules=10, device=torch.device('cpu'))
    state.update_dopamine(current_loss=1.0)
    # Baseline initialises to 0, so dopamine = sensitivity * (1.0 - 0) > 0
    assert state.current_dopamine > 0


def test_neuromodulation_exploration_bonus_shape(small_config):
    """Exploration bonus has shape (num_modules,)."""
    cfg = small_config.neuromodulation
    state = NeuromodulationState(cfg, num_modules=10, device=torch.device('cpu'))
    state.update_dopamine(current_loss=1.5)
    bonus = state.get_exploration_bonus()
    assert bonus.shape == (10,)


def test_neuromodulation_adaptive_temperature(small_config):
    """Adaptive temperature grows with positive dopamine."""
    cfg = small_config.neuromodulation
    cfg.enabled = True
    state = NeuromodulationState(cfg, num_modules=10, device=torch.device('cpu'))
    state.update_dopamine(current_loss=5.0)   # high loss → high dopamine
    base = 1.0
    temp = state.get_adaptive_temperature(base)
    assert temp >= base  # surprise should push temperature up
