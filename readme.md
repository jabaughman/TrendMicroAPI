This program allows the use of TrendMicro API to pull endpoint detection and response logging

-----------------------------------------

The logfeeder.ini file needs to be configure with the Access and Secret Tokens, which can be found in AWS Secrets Manager in BF-Main as LogFeeder.
There is also a public key that needs to be applied and should live under the secrets directory. 
This key can be found under LogFeederPubKey in AWS Secrets Manager.

Main.py uses boto3 to upload log files to S3. Make sure to add in the appropriate access and secret keys here:
AWS_ACCESS_KEY = 'xxxxxxxxxxx'
AWS_SECRET_KEY = 'xxxxxxxxxxx'

---

To-do:
Use AWS Secrets Manager to load AWS Credentials instead of statically in code.
