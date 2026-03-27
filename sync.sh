rsync -arv pyproject.toml jagoda.mm:/opt/home-display/pyproject.toml
rsync -arv \
 --exclude '__pycache__/' \
 --exclude '.DS_Store' \
 --exclude 'çache/' \
 src/ jagoda.mm:/opt/home-display/inky/
