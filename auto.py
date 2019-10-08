import os
import argparse
import sys
import time
import subprocess
import pysftp

def get_parameter():
    parser = argparse.ArgumentParser()
    parser.add_argument('-input_file', type=str, help='input file .avs yang akan digunakan.')
    parser.add_argument('-scale', type=str, help='resolusi video, dalam format x:y. Contohnya 1280:720 untuk 720p, 1280:-1 untuk lebar 1280 dengan tinggi menyesuaikan aspek rasio.')
    parser.add_argument('-destinasi_file', type=str, help='lokasi folder tempat hasil akan disimpan. File dibuat disini, pastiin ada dulu foldernya.')
    parser.add_argument('-crf', type=float, help='crf yang akan digunakan video encoder, default 22.')
    parser.add_argument('-aq_str', type=float, help='aq-strength yang akan digunakan video encoder, default 1.')
    parser.add_argument('-aq_mode', type=int, help='aq-strength yang akan digunakan video encoder, default 3.')
    parser.add_argument('-thread', type=int, help='jumlah yang akan digunakan video encoder.')
    parser.add_argument('-hevc', action='store_true', help='pakai HEVC, kalau ini gak dimasukin cuma pake x264.')
    parser.add_argument('-aac', action='store_true', help='pakai AAC, kalau ini gak dimasukin bakal pake OPUS.')
    parser.add_argument('-sftp', action='store_true', help='nyalakan fitur upload via sftp.')
    parser.add_argument('-attach', type=str, help='tambahkan attachment font.')
    params = parser.parse_args().__dict__
    params = check_parameter(params)
    return params
    
# Cek input file, destinasi folder
def check_parameter(params):
    if params['input_file']:
        params['input_dir'] = os.path.dirname(os.path.abspath(params['input_file']))
        params['orig_dir'] = os.path.abspath(os.path.curdir)
    else:
        raise FileNotFoundError('File tidak ada')

    # if params['destinasi_file']:
    #     dest_path = os.path.abspath(params['destinasi_file'])
    #     if not os.path.exists(dest_path):
    #         raise FolderNotFoundError('Folder destinasi tidak ada: %s' % (dest_path))
    #     if not os.path.isfile(params['input_file']):
    #         raise FileNotFoundError('File tidak ada: %s' % (params['input_file']))
    #print('ALL PARAMS OK')

    if params.get('scale') and len(params['scale'].split(':')) == 2:
        params['scale'] = params['scale'].split(':')
        params['scale'] = [x.replace('0', '-1') if len(x) == 1 else x for x in params['scale']]

    # Default aq-mode
    if params['aq_mode']:
        if params['aq_mode'] > 3 or params['aq_mode'] < 0:
            print('Nilai aq-mode diluar spesifikasi encoder. Akan mengembalikan default ke 3.')
            params['aq_mode'] = 3
        pass
    else:
        params['aq_mode'] = 3

    # Default aq-strength
    if params['aq_str']:
        if params['aq_str'] < 0 or params['aq_str'] >3.0 :
            print('Nilai aq-strength diluar spesifikasi encoder. Akan mengembalikan default ke 1.')
            params['aq_str'] = 1.0
        pass
    else:
        params['aq_str'] = 1.0

    # Default CRF
    if params['crf'] is None:
        params['crf'] = 22.0

    return params

def start_process(params):
    # Filter video
    # video_filters = list()
    video_filters = ''
    # Filter untuk rescale size
    # if params['scale']:
    #    video_filters.append(('scale={width}:{height}'.format(width=params['scale'][0], height=params['scale'][1])))
    
    ## Cek audio mau pakai aac atau opus
    if params['aac']:
        audio_encoder = '-c:a libfdk_aac -vbr 4'
    else:
        audio_encoder = '-c:a libopus -b:a 96k -vbr on -compression_level 10'
    
    if params['thread'] is not None:
        thread = params['thread']
    else:
        thread = 0

    if params['hevc']:
        ## Parameter x265, edit seperlunya. 
        video_encoder = '-c:v libx265 -threads {thread} -preset slower -pix_fmt yuv420p10le -x265-params ctu=32:crf={crf}'\
        ':psy-rd=2.0:psy-rdoq=2.00:aq-mode={aqmode}:aq-strength={aqstr}:me=3:bframes=8:ref=6:sao=0:selective-sao=0:ctu=32:rd=4:subme=5'\
        ':rect=1:amp=0:rc-lookahead=30:limit-refs=2:max-merge=3:rskip=1:tu-intra-depth=2:tu-inter-depth=2:lookahead-slices=4:pools={thread}'\
            .format(crf=params['crf'],aqmode=params['aq_mode'], aqstr=params['aq_str'], thread=params['thread'])
    
    else:
        ## Parameter x264, edit seperlunya
        video_encoder = '-c:v libx264 -threads {thread} -preset veryslow -pix_fmt yuv420p10le -crf {crf} -aq-mode {aqmode} -aq-strength {aqstr}'\
            .format(crf=params['crf'],aqmode=params['aq_mode'], aqstr=params['aq_str'], thread=params['thread'])
    
    ## Finishing parameter untuk ffmpeg
    if not video_filters:
        ffmpeg_params = 'ffmpeg -i \"{input_file}\" {filters} {video} {audio} \"{destinasi}\"'\
            .format(input_file=params['input_file'],filters=video_filters, crf=params['crf'],aq_mode=params['aq_mode'], aq_strength=params['aq_str'], destinasi=params['destinasi_file'], audio=audio_encoder, video=video_encoder)
    else:
        ffmpeg_params = 'ffmpeg -i \"{input_file}\" {video} {audio} \"{destinasi}\"'\
            .format(input_file=params['input_file'],filters=video_filters, crf=params['crf'],aq_mode=params['aq_mode'], aq_strength=params['aq_str'], destinasi=params['destinasi_file'], audio=audio_encoder, video=video_encoder)

    ## print('PROCESS')
    print(ffmpeg_params)
    print('_' * 50 + '\n')
    # Start calling external process FFMPEG for encoding
    process = subprocess.Popen(ffmpeg_params, shell=True, stdout=subprocess.PIPE)

    for line in iter(process.stdout.readline, b''):
        line = line.decode('utf8')

        try:
            sys.stdout.write(line)
            tempfile.write(line)
        except:
            pass

    print('_' * 50 + '\n' + '_' * 50 + '\n')
    
    
    # Connect to SFTP server and upload file
    if params['sftp']:
        print("Uploading file to FTP SERVER")
        # accept any host key (warning, this will make YOU invurnerable to MITM attack! use at your own risk!)
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        temp_dest = "{0}".format(params['destinasi_file'])
        # temp_dest = temp_dest.replace("\\\\","\\")
        print (temp_dest)
        # attempt connection
        server = pysftp.Connection(host="x",username="x",password="x", log="ftp.log", cnopts=cnopts)
        with server.cd('/path/to/destination'):
            server.put(temp_dest)
        server.close()

    # No error check so far, if any error occurs it must be handled manually.

    print("SUCCESSFULLY PROCESSED BY FFMPEG AND UPLOADED TO DESTINATION HOST")
    print('_' * 50 + '\n' + '_' * 50 + '\n')

if __name__ == '__main__':
    ## Validasi parameter
    params = get_parameter()
    print('Proses file ' + params['input_file'])
    print('_' * 50 + '\n' + '_' * 50 + '\n')
    print('Starting external job...\n[%s]' % "ffmpeg")
    print('_' * 50 + '\n' + '_' * 50 + '\n')
    start_process(params)