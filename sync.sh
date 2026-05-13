rsync -arv pyproject.toml jagoda.mm:/opt/home-display/pyproject.toml
rsync -arv \
 --exclude '__pycache__/' \
 --exclude '.DS_Store' \
 --exclude 'cache/' \
 --exclude '*.egg-info/' \
 src/ jagoda.mm:/opt/home-display/inky/
