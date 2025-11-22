rsync -arv requirements.txt jagoda.mm:/opt/home-display/
rsync -arv \
 --exclude '__pycache__/' \
 --exclude '.DS_Store' \
 --exclude 'çache/' \
 src/ jagoda.mm:/opt/home-display/inky/
