from bert4keras.backend import keras, set_gelu
from bert4keras.models import build_transformer_model


set_gelu("tanh")


def textcnn(inputs, kernel_initializer):
    """
    基于keras实现的textcnn
    :param inputs:
    :param kernel_initializer:
    :return:
    """
    # 3,4,5
    """
        1. 这个模型定义了一个基于 TextCNN（Text Convolutional Neural Network）的文本分类模型，使用 Keras 框架实现。
        2. 输入 inputs 是一个 3D 张量，其形状为 (batch_size, sequence_length, embedding_size)，
            其中 batch_size 表示输入的样本数，sequence_length 表示输入的序列长度，embedding_size 表示每个词语的嵌入向量维度。
        3. 模型包含 3 个卷积层，每个卷积层的输出特征图数量均为 256。卷积核大小分别为 3、4 和 5，步长为 1，填充方式为 'same'，激活函数为 ReLU。
        4. 对于每个卷积层，经过卷积操作后得到一个形状为 (batch_size, sequence_length - kernel_size + 1, num_filters) 的特征图，其中 kernel_size 为卷积核大小，num_filters 为输出特征图数量。接着，对每个特征图使用全局最大池化操作，将每个特征图的最大值保留下来，形成一个长度为 num_filters 的向量。这样，每个卷积层最终的输出形状为 (batch_size, num_filters)。
        5. 然后，将 3 个卷积层的输出特征向量连接起来，形成一个长度为 3 * num_filters 的向量。接着使用一个 Dropout 层来防止过拟合，并将最终的输出结果返回。

        总之，这个模型使用卷积层来提取输入序列的局部特征，然后将不同卷积核的输出特征进行拼接，得到整个序列的特征表示，最终通过全连接层将其映射到分类标签上。
        由于卷积层对于输入序列的平移具有不变性，因此 TextCNN 模型在文本分类等任务上表现出较好的性能。
    """
    cnn1 = keras.layers.Conv1D(256,
                               3,
                               strides=1,
                               padding='same',
                               activation='relu',
                               kernel_initializer=kernel_initializer)(inputs)  # shape=[batch_size,maxlen-2,256]
    cnn1 = keras.layers.GlobalMaxPooling1D()(cnn1)

    cnn2 = keras.layers.Conv1D(256,
                               4,
                               strides=1,
                               padding='same',
                               activation='relu',
                               kernel_initializer=kernel_initializer)(inputs)
    cnn2 = keras.layers.GlobalMaxPooling1D()(cnn2)

    cnn3 = keras.layers.Conv1D(256,
                               5,
                               strides=1,
                               padding='same',
                               kernel_initializer=kernel_initializer)(inputs)
    cnn3 = keras.layers.GlobalMaxPooling1D()(cnn3)

    output = keras.layers.concatenate([cnn1, cnn2, cnn3], axis=-1)
    output = keras.layers.Dropout(0.2)(output)

    return output


def build_bert_model(config_path, checkpoint_path, class_nums):
    """
    构建bert模型用来进行医疗意图的识别
    :param config_path:
    :param checkpoint_path:
    :param class_nums:
    :return:
    """
    # 预加载bert模型
    bert = build_transformer_model(
        config_path=config_path,
        checkpoint_path=checkpoint_path,
        model='bert',
        return_keras_model=False
    )

    # 抽取cls 这个token
    cls_features = keras.layers.Lambda(
        lambda x: x[:, 0],  # 所有行的第一列
        name='cls-token')(bert.model.output)  # shape=[batch_size,768]
    # 抽取所有的token，从第二个到倒数第二个
    all_token_embedding = keras.layers.Lambda(
        lambda x: x[:, 1:-1],
        name='all-token')(bert.model.output)  # shape=[batch_size,maxlen-2,768]

    cnn_features = textcnn(all_token_embedding, bert.initializer)  # shape=[batch_size,cnn_output_dim]

    # 特征拼接
    concat_features = keras.layers.concatenate([cls_features, cnn_features], axis=-1)

    dense = keras.layers.Dense(units=512,
                               activation='relu',
                               kernel_initializer=bert.initializer)(concat_features)

    output = keras.layers.Dense(units=class_nums,
                                activation='softmax',
                                kernel_initializer=bert.initializer)(dense)

    model = keras.models.Model(bert.model.input, output)
    # print(model.summary())

    return model
