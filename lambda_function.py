#
# Copyright Amazon.com, Inc. and its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT
#
# Licensed under the MIT License. See the LICENSE accompanying this file
# for the specific language governing permissions and limitations under
# the License.
#

import requests, boto3
from requests_aws4auth import AWS4Auth
import cfnresponse

def lambda_handler(event, context):
  print(event)
  try:
    if event['RequestType'] == 'Create':
      region = event['ResourceProperties']['Region']
      host = event['ResourceProperties']['Host']

      service = 'es'
      credentials = boto3.Session().get_credentials()
      awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

      repo = 'https://raw.githubusercontent.com/aws-samples/aws-waf-ops-dashboards/main/'

      filenames = ['awswaf-es-index-template.json']
      headers={'kbn-xsrf': 'true', 'Content-Type': 'application/json'}
      for filename in filenames:
        f = requests.get(repo + filename).content
        url = 'https://{}/_template/date_template?pretty'.format(host)
        r = requests.put(url, auth=awsauth, headers=headers, data=f)
        #if r.status_code != 200: 
        #    raise RuntimeError('Failed configuring Elasticsearch - file: {}, status: {}, message: {}'.format(filename, r.status_code, r.content))
        print(filename, r.status_code, r.content)

      filenames = ['awswaf-es-index.ndjson', 'awswaf-es-visualizations.ndjson', 'awswaf-es-dashboards.ndjson']
      headers={'kbn-xsrf': 'true'}
      for filename in filenames:
        f = requests.get(repo + filename).content
        url = 'https://{}/_plugin/kibana/api/saved_objects/_import?overwrite=true'.format(host)
        r = requests.post(url, auth=awsauth, headers=headers, files={ 'file': (filename, f) })
        #if r.status_code != 200: 
        #    raise RuntimeError('Failed configuring Elasticsearch - file: {}, status: {}, message: {}'.format(filename, r.status_code, r.content))
        print(filename, r.status_code, r.content)

      print('Successfully configured Kibana')
      cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
      return
    elif event['RequestType'] in ['Delete', 'Update']:
      cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
      return
  except Exception as err:
    print(err)
    cfnresponse.send(event, context, cfnresponse.FAILED, {})
    return
