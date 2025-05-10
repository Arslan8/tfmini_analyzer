# tfmini_analyzer
Sure! Here's the `README.md` in proper Markdown format:


# tfmini_analyzer

**Python-based UART analyzer for the TFMini-S LiDAR using the Saleae Logic 2 Automation API.**

## Overview

`tfmini_analyzer` is a tool designed to automate the capture and analysis of UART data from the [TFMini-S Micro LiDAR Module]([https://www.benewake.com/en/tfmini.html](https://www.sparkfun.com/tfmini-s-micro-lidar-module.html)) using a [Saleae Logic Pro 8]((https://www.saleae.com/products/saleae-logic-pro-8)) device. It helps extract and interpret distance measurements and signal quality information.



## Requirements

- **Hardware**
  - TFMini-S Micro LiDAR module
  - Saleae Logic device (e.g., Logic Pro 8)

- **Software**
  - [Saleae Logic 2](https://www.saleae.com/downloads/) with Automation API enabled
  - Python 3.8+
  - Logic2 Python automation package

## Installation
```bash
git clone https://github.com/Arslan8/tfmini_analyzer.git
cd tfmini_analyzer
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

1. **Connect TFMini-S TX to Logic analyzer digital input (e.g., D3). Make sure you have a common ground.**
2. **Start Saleae Logic 2 with Automation API enabled. You can enable the automation server by going to ```Edit->Settings->Enable Automation Server```.**
3. **Run the script**

```bash
python analyzer.py
```

By default, it captures from digital channel 3 at 10 MHz with a 1.2V threshold. You can modify this in `analyzer.py`.

## Example Output

```text
(logic) abk6349@e5-cse-359-01:~/data/logic/tfmini_analyzer$ python3 ./analyzer.py 
INFO:saleae.automation.manager:sub ChannelConnectivity.IDLE
INFO:saleae.automation.manager:sub ChannelConnectivity.CONNECTING
INFO:saleae.automation.manager:sub ChannelConnectivity.READY
[0] OK  - Distance: 17 cm, Strength: 5026, Temp: 53.0 °C
[9] OK  - Distance: 17 cm, Strength: 5027, Temp: 53.0 °C
[18] OK  - Distance: 17 cm, Strength: 5033, Temp: 53.0 °C
[27] OK  - Distance: 17 cm, Strength: 5040, Temp: 53.0 °C
[36] OK  - Distance: 17 cm, Strength: 5032, Temp: 53.0 °C
[45] OK  - Distance: 17 cm, Strength: 5033, Temp: 53.0 °C
```

Feel free to reach out with any questions. 
