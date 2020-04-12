

def init():

    model = sent2vec.Sent2vecModel()
    model.load_model('../wiki_bigrams.bin')
    return model
