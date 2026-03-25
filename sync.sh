rsync -arv requirements-prod.txt jagoda.mm:/opt/home-display/requirements.txt
rsync -arv \
 --exclude '__pycache__/' \
 --exclude '.DS_Store' \
 --exclude 'çache/' \
 src/ jagoda.mm:/opt/home-display/inky/
