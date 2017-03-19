import boto3
import sys, time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import random
import pandas as pd
import io
import os

NAMESPACE = os.environ['NAMESPACE']
METRICNAME = os.environ['METRICNAME']
TARGET_S3_BUCKET = os.environ['TARGET_S3_BUCKET']
TARGET_S3_KEY = os.environ['TARGET_S3_KEY']
AWS_REGION = os.environ['AWS_REGION']

client = boto3.client('cloudwatch', region_name=AWS_REGION)

def handler(event, context):
    u = client.get_metric_statistics(
            Namespace=NAMESPACE,
            MetricName=METRICNAME,
            Period=60*20,
            Statistics=['Maximum'],
            StartTime=datetime.utcnow() - timedelta(days=14),
            EndTime=datetime.utcnow())

    print repr(u)

    events = {}
    timestamps = []
    
    for datapoint in u['Datapoints']:
        ts = datapoint['Timestamp']
        timestamps.append(ts)
        events[ts] = datapoint['Maximum']

    timestamps = sorted(timestamps)
    sevents = [ events[x] for x in timestamps ]
    dtimestamps = [ x for x in timestamps ]

    dic = { 'date': dtimestamps, 'events': sevents }

    df = pd.DataFrame.from_dict(dic)
    print(df.describe())

    patt = df.set_index('date')
    #patt_sampled = patt.resample('T').sum()
    patt_sampled = patt

    patt_plot = patt_sampled.plot(title="Remaining",legend=None)
    fig = patt_plot.get_figure()
    #fig.savefig("remaining.png")
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    contents = buf.read()
    buf.close()

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(TARGET_S3_BUCKET)
    day = datetime.strftime(datetime.now(), "%Y%m%d")
    day = "latest"
    bucket.Object('{}/{}.png'.format(TARGET_S3_KEY, day)).put(Body=contents)


#handler(None, None)
