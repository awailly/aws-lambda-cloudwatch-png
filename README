Lamda function to get metric statistics from CloudWatch and save as a PNG to s3
===

Setup the ec2 environment
---

sudo yum -y install python27-devel python27-pip gcc
sudo yum -y install freetype-devel
sudo yum -y install libpng-devel
virtualenv ~/env
source ~/env/bin/activate

pip install pandas matplotlib

Full ZIP generation
---

zip -r9 ~/generateGraph.zip *
cd $VIRTUAL_ENV/lib/python2.7/site-packages
zip -r9 ~/generateGraph.zip *
cd $VIRTUAL_ENV/lib64/python2.7/site-packages

Update the function
---

zip -g generateGraph.zip graphPMET.py
aws lambda update-function-code --function-name generatePNGfromCloudwatch --zip-file fileb://generateGraph.zip --region eu-west-1

Useful links
---

http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-deployment-pkg.html#with-s3-example-deployment-pkg-python
http://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html
http://stackoverflow.com/questions/34749806/using-moviepy-scipy-and-numpy-in-amazon-lambda
