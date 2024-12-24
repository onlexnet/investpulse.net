# entrypoint script to run other initialization scripts
# The script is invoked per bash automatically thanks to settings.json

# load original settings
# it is required as we invoked the script using --rcfile settin and it also disable automatic loading ~/.bashrc script when new shell is created
. ~/.bashrc

. init-envs.sh