from flask import Flask, render_template, send_from_directory
import pandas as pd

app = Flask(__name__)

@app.route('/pullups_history')
def result():
    hist_df = pd.read_csv("../db.csv")
    hist_list = hist_df.values.tolist()
    print(hist_df.shape)
    return render_template('pullups_history.html', pullup_sessions = hist_list)

@app.route('/videos/<filename>')
def uploaded_file(filename):
   return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.config['DOWNLOAD_FOLDER'] = '/home/mendel/mnt/resources/videos/'
    app.run(debug = True, port=1234, host='0.0.0.0')