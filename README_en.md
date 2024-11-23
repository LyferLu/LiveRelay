[[English](README_en.md)] [[简体中文](README.md)]

## Introduction

A live stream relay script based on the powerful [Streamlink](https://streamlink.github.io), capable of seamless live stream relaying between platforms such as YouTube and Twitch.

## Supported Platforms

- [x] YouTube
- [x] Twitch

## Usage

### Running from Source

```sh
# Clone the source code
git clone https://github.com/LyferLu/LiveRelay.git
cd LiveRelay
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Run from source
python main.py
```

## Configuration

The configuration file is stored in `config.json`, located in the same directory as the executable.

After modifying the sample configuration file [`config.sample.json`](config.sample.json), be sure to rename it to `config.json`.

The file content must strictly follow JSON syntax. Please validate it on an online JSON formatter before making modifications.

### Relay Address

Modify the `RTMPServer` field according to the example.

### Live Stream Configuration

Modify the `streams` list according to the example. Pay attention to commas, quotes, and indentation.

| Field    | Meaning              | Possible Values                              | Required | Remarks                                                      |
| -------- | -------------------- | -------------------------------------------- | -------- | ------------------------------------------------------------ |
| platform | Live platform        | The English name of the live platform        | Required | Case insensitive                                             |
| id       | Live user ID         | Room number or username of the live platform | Required |  |
| name     | Custom streamer name | Any characters                               | Optional | Used to distinguish recorded files<br/>Defaults to ID if not provided |
| index    | Index priority       | Integer                                      | Required | The smaller the index, the higher the priority               |

#### YouTube Channel ID

The YouTube channel ID usually starts with `UC` followed by a string of characters. Since YouTube allows custom identifiers, the URL will prioritize displaying the identifier instead of the channel ID.

You can use the following websites to get the YouTube channel ID:

[https://seostudio.tools/en/youtube-channel-id](https://seostudio.tools/en/youtube-channel-id)

[https://ytgear.com/youtube-channel-id](https://ytgear.com/youtube-channel-id)

## Acknowledgements

[https://github.com/auqhjjqdo/LiveRecorder](https://github.com/auqhjjqdo/LiveRecorder)

[https://github.com/gav-X/RepushStream](https://github.com/gav-X/RepushStream)