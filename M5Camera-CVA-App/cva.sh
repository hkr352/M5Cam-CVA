#!/bin/sh

APIKEY=$2
IMAGE_PATH_IN=$1
IMAGE_PATH_OUT="temp/image_out.base64"
base64 ${IMAGE_PATH_IN} > ${IMAGE_PATH_OUT}
REQESTJSON=temp/reqest.json

#LABEL_DETECTION
#OBJECT_LOCALIZATION

cat << EOF > ${REQESTJSON}
{
  "requests":[
    {
      "image":{
        "content":"`cat ${IMAGE_PATH_OUT}`"
      },

      "features":[
        {
          "type":"LABEL_DETECTION",
          "maxResults":5
        },
        {
          "type":"TEXT_DETECTION",
          "maxResults":1
        },
      ]
    }
  ]
}
EOF

curl -k -s -H "Content-Type: application/json" \
https://vision.googleapis.com/v1/images:annotate?key=${APIKEY} \
--data-binary @${REQESTJSON} -o response.json

rm -f "$image_out.base64"
rm -f "$reqest.json"