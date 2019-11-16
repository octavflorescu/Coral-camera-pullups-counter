# download the model 
wget https://github.com/google-coral/edgetpu/raw/master/test_data/mobilenet_v1_1.0_224_l2norm_quant_edgetpu.tflite
# setup the training data: a folder containing subfolders /each class
# dataset
#   -- class1
#   ----img.png
#   ----img2.png
#   -- class2
#   ----img.png
# Start the imprinting
python3 imprinting_learning.py \
 --model_path ./mobilenet_v1_1.0_224_l2norm_quant_edgetpu.tflite \
 --data $HOME/mnt/resources/face_classes_dataset \
 --output $HOME/mnt/imprinting_classification/retrained_imprinting_model.tflite

# test
python3 classify.py \
 --model retrained_imprinting_model.tflite \
 --label retrained_imprinting_model.txt \
 --image $HOME/mnt/resources/face_classes_dataset/octavf/15-11-2019_15-40-41.png
