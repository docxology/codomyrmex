#!/bin/bash
pnpm start &
echo $! > app.pid
