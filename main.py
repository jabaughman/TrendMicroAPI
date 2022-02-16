import boto3
import glob
import os
import os.path
import subprocess
import logging
from botocore.exceptions import ClientError
from logfeeder import LogFeeder

AWS_ACCESS_KEY = 'xxxxxxxxxxx'
AWS_SECRET_KEY = 'xxxxxxxxxxx'
target_dir = '/tmp/TrendMicro/'

def lambda_handler():
    client = LogFeeder()
    S3_BUCKET = 'trendmicro-test-bucket-cybersec'
    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_SECRET_KEY)

    try:
        print "query logs start: "
        client.query_logs()

        """extract all 7zip files in /tmp/TrendMicro/ directory"""
        p = subprocess.Popen(["7za", "x", "/tmp/TrendMicro/", "-prapid7", "-r", "-o/tmp/TrendMicro"],
                             stdout=subprocess.PIPE)
        output, err = p.communicate()
        print("***Running extraction of files with pza***"), output

        """Clean up .7z artifacts before pushing logs to S3"""
        filelist = glob.glob(os.path.join(target_dir, "*.7z"))
        for f in filelist:
            os.remove(f)

        for filename in os.listdir(target_dir):
            logging.warn('Uploading %s to Amazon S3 Bucket %s' % (filename, S3_BUCKET))
            s3.Object(S3_BUCKET, filename).put(Body=open(os.path.join(target_dir, filename), 'rb'))

    except ClientError as e:
        print ("Failed to query logs from trend API")
        logging.error(e)
        return False
    return True


if __name__ == '__main__':
    lambda_handler()

    """Cleanup /tmp/TrendMicro/ so I don't have duplicates"""
    file_list = glob.glob(os.path.join(target_dir, "*.log"))
    for fl in file_list:
        print("removing file", fl)
        os.remove(fl)