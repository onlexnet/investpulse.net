# load original settings
# it is required as we use --rcfile setting usgin the scripts,its also disable automatic loading ~/.bashrc script when new shell is created
. ~/.bashrc

# apply additional changes

 # automatically export all variables
set -a
source .env
set +a
