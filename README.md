## Competitive Structured Data Analysis

#### First Test
1. Clone repo
2. Make .sh into execuitable `chmod +x start.sh`
3. Run `./run.sh`

**Above will only work on linux / unix os. Will have to install dependencies manually and run with `python main.py` if on Windows (unless using WSL on Windows to run).

#### Custom Job (*Assuming Repo Already Cloned / `start.sh` > Exe)
1. Update `input.csv` with desired client / competitors
   1. Max 25 per domain (hard coded into script)
   2. Sync runs asyncio - which can use your os to make a lot of requests very very quickly
   3. This is to protect website servers, as too many concurrent requests can hurt websites
2. Update the `config.yaml` 
3. Run `./run.sh`
