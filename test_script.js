const context = {
  ref: "refs/pull/121/merge",
  eventName: "pull_request"
};
const ref = context.eventName === 'pull_request' ? process.env.GITHUB_HEAD_REF : context.ref.replace('refs/heads/', '');
console.log(ref);
