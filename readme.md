# Logistics Accrual

purpose of automation project is to 

repository is located at : https://gitea_qa.s2.ms.unilever.com:3000/gnanadeep/Logistics_Accruals
documetation is located at @todo

## General Description
   
* Environment
      * Windows 11
      * 64-bit OS, x64-based processor
      * Python 3.10+

## running from consol

I code is run via consol comend then 

```commandline
# py cli.py --mef mef --input_file input_file --forex forex --country country --plant plant --date date

python '.\cli.py' --json_path "" --input_path "" --output_path ""
```

## instalation 

```
py -3.10 -m venv env
env\scripting\activate
py -m pip install -r requirements.txt
py -m pip install --upgrade pip
```

During development any new dependence should be saved to `\\s2.ms.unilever.com\dfs\ES-GROUPS\cor\frd\UFO-General\INTERFACE\UPIT\pypi\`
so deployment scripts can install od prod/qa

```command
py -m pip download -r requirements.txt -d \\s2.ms.unilever.com\dfs\ES-GROUPS\cor\frd\UFO-General\INTERFACE\UPIT\pypi\
```
