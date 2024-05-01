# Agents

Each agent is responsible for
- Keep budget behalf of the Client
- Plan and execute buy and sell operations when possible as close as requested orders
- Inform the CLient when operation is finished or cancelled


## Development environment
Central point is .env file. It is required, as - in opposit to use DAPR in 'normal' way when it sets some variables out of the box - we have to set such variables for DAPR and for the service as well to keep them in sync.
We have 4 scenarios:
1) run tests usin mvn clean install from shell,
2) run tests from vscode directly
3) run service locally using vscode
4) run service as part of wholde solution with other services

For all of such cases we have a bit different way how .env file is consumed
1) for shell: variables are set each time when new shell is created thanks to .init.sh file (see settings.json)
2) test in vscode uses .ven thanks to settings.json **"envFile": "${workspaceFolder}/.env"** in *java.test.config section*
3) service runs with .env variables thanks to launch.json **"envFile": "${workspaceFolder}/.env"** in *configurations*
4) when started as part of whole solution, all env variables are expected as part of the big run.
