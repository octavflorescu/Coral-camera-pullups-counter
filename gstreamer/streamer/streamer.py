from flask import Flask, render_template, send_file
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath('/home/mendel/mnt/cameraSamples/examples-camera/gstreamer'))
from definitions import CONSTANTS

app = Flask(__name__, static_folder='static')


@app.route("/")
@app.route('/pullups_history')
def result():
    if os.path.exists(CONSTANTS.db_path):
        hist_df = pd.read_csv(CONSTANTS.db_path, names=CONSTANTS.PullupsHistoryColumns.all_ordered)
        hist_df[CONSTANTS.PullupsHistoryColumns.EVIDENCE] = hist_df[CONSTANTS.PullupsHistoryColumns.EVIDENCE].apply(lambda x: x.split('/')[-2])
        hist_list = hist_df.values.tolist()
        print(hist_df.shape)
    else:
        hist_list = ["no history"]
    return render_template('pullups_history.html', pullup_sessions=hist_list)


@app.route('/videos/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    print(filename)
    # return render_template('video.html', video_path='video.mpg')
    return send_file('{}{}/video.mpg'.format(app.config['DOWNLOAD_FOLDER'], filename),
                     attachment_filename='video.mpg',
                     as_attachment=True)


if __name__ == '__main__':
    app.config['DOWNLOAD_FOLDER'] = '/home/mendel/mnt/resources/videos/'
    app.run(debug=True, port=1234, host='0.0.0.0')

