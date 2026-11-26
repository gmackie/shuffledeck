#!/bin/sh
set -eu
cd "$(dirname "$0")"
exec wrangler pages deploy site --project-name shuffledeck --branch main "$@"
