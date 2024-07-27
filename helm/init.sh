# entrypoint script to rune other initialization scripts

# load original settings
# it is required as we use --rcfile setting usgin the scripts,its also disable automatic loading ~/.bashrc script when new shell is created
. ~/.bashrc

. init-k8s.sh
. init-envs.sh