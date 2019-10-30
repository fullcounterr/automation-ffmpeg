# automation-ffmpeg
Hello, this script is made for me to make encoding job easier by automating encode and post update. This works really well with proper RSS feed setup.

To run the program, there are some prerequisite dependency to install :

pip install pysftp requests

You also need to specify ffmpeg installation path in your PATH environment variable.
Currently you can run main.py with the following command :

## main.py
main.py -spath <source_path> -dpath <destination_path> [-sftp]

|Parameter|Description|
|----------------|-------------------------------|
|-spath |Source path where the program will watch for change          |
|-dpath |Destination path where processed file will be placed. This must be different than -spath.           |
|-sftp |Enable this if you want to enable FTP upload and automatic post update.|

The required parameter for the program to work correctly is to include -spath and -dpath. -sftp is optional.

main.py will run auto.py with a parameter prebuilt at on_created() function which have -input_file, -hevc -aq_str, -thread, and -destinasi_file, with -sftp and -apost being optional if you enable -sftp on main.py parameter.

## auto.py

|Parameter|Description|
|----------------|-------------------------------|
|-input_file |Source file path for the program to process, including file name and extension.          |
|-scale|Rescale video with x:x format. Currently broken.           |
|-destinasi_file|Destination path for processed file, including file name and extension.|
|-crf|CRF value. Default 22.|
|-aq_str|AQ strength value. Default 1.0.|
|-aq_mode|AQ mode value. Default 3.|
|-thread|Number of thread for ffmpeg to use. Default 6.|
|-hevc|Enable HEVC (x265) instead of x264.|
|-aac|Enable AAC instead of OPUS.|
|-sftp|Enable file upload using SFTP.|
|-apost|Enable automatic post update via REST API.|
|-attach|Attach file to encoded file. Currently broken.|

auto.py need at least -input_file and -destinasi_file to work with default settings.

### REGEX usage

Currently the 2 included regex supports fansub standard file naming with and without CRC.
For example :

    [HorribleSubs] What anime name - 02 [1080p].mkv
    [Chyuu] Whatever name is this - 02 [1080p][CRCVALUE].mkv

Using the regex, you can disassemble file name to, for example, python dictionary with format :

    ['Chyuu', 'Whatever name is this, '02', '1080p', 'CRCVALUE', '.mkv']
    
This will be used for craft new file name in main.py and auto.py.
