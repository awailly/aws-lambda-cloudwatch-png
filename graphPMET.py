import boto3
import sys, time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import random
import pandas as pd
import io
import os

NAMESPACE = os.environ['NAMESPACE']
TARGET_S3_BUCKET = os.environ['TARGET_S3_BUCKET']
TARGET_S3_KEY = os.environ['TARGET_S3_KEY']
AWS_REGION = os.environ['AWS_REGION']
GRAPH_TITLE = os.environ['GRAPH_TITLE']

client = boto3.client('cloudwatch', region_name=AWS_REGION)

def get_metric_dic(metric_name):
    u = client.get_metric_statistics(
            Namespace=NAMESPACE,
            MetricName=metric_name,
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

    dic = { 'date': dtimestamps, metric_name: sevents }

    return dic
    #df = pd.DataFrame.from_dict(dic)
    #print(df.describe())
    #return df

def handler(event, context):
    u = client.list_metrics(Namespace=NAMESPACE)
    print(repr(u))
    data_frames = []

    for metric_name in u['Metrics']:
        df = get_metric_dic(metric_name['MetricName'])
        data_frames.append(df)

    #df = pd.concat(data_frames)

    dic = {}
    for dfi in data_frames:
        for key in dfi:
            dic[key] = dfi[key]

    df = pd.DataFrame.from_dict(dic)

    print(df)
    print(df.describe())

    patt = df.set_index('date')
    #patt_sampled = patt.resample('T').sum()
    patt_sampled = patt

    plt.style.use('classic')
    patt_plot = patt_sampled.plot(title=GRAPH_TITLE, legend=True, marker='v')
    patt_plot.autoscale(False)
    patt_plot.set_ylim(ymin=0)
    #patt_plot.xaxis.set_minor_locator(dates.WeekdayLocator(byweekday=(1), interval=1))
    #patt_plot.xaxis.grid(True, which="minor")
    patt_plot.xaxis.set_major_formatter(dates.DateFormatter("%m/%d"))
    patt_plot.set_xlabel('')
    lgd = patt_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=5)
    patt_plot.yaxis.grid(True)
    patt_plot.xaxis.grid(True)
    #patt_plot.xaxis.set_major_locator(dates.MonthLocator())
    #patt_plot.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b\n%Y'))
    #plt.tight_layout()
    fig = patt_plot.get_figure()
    #fig.savefig("remaining.png")
    buf = io.BytesIO()
    fig.savefig(buf, bbox_extra_artists=(lgd,), bbox_inches='tight')
    buf.seek(0)
    contents = buf.read()
    buf.close()

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(TARGET_S3_BUCKET)
    day = datetime.strftime(datetime.now(), "%Y%m%d")
    day = "latest"
    bucket.Object('{}/{}.png'.format(TARGET_S3_KEY, day)).put(Body=contents)


#handler(None, None)
