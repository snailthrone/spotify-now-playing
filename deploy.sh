cd package
zip -r9 ${OLDPWD}/spotify-now-playing.zip .
cd $OLDPWD
zip -g spotify-now-playing.zip lambda_function.py
