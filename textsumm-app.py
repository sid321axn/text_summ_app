from flask import Flask, render_template, request
import bs4 as bs  
import urllib.request  
import re
import nltk

app = Flask(__name__)


@app.route('/index.html', methods=['GET', 'POST'])

def index():
    errors = []
    results = {}
    if request.method == "POST":
        # get url that the person has entered
        try:
            url = request.form['url']
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return render_template('index.html', errors=errors)
        if r:
            scraped_data = urllib.request.urlopen(url)  
            article = scraped_data.read()
            parsed_article = bs.BeautifulSoup(article,'lxml')
            paragraphs = parsed_article.find_all('p')
            article_text = ""

            for p in paragraphs:  
                article_text += p.text
            # Removing Square Brackets and Extra Spaces
            article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)  
            article_text = re.sub(r'\s+', ' ', article_text)  
            # Removing special characters and digits
            formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )  
            formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)  
            # stop words
            nltk.download('punkt')
            sentence_list = nltk.sent_tokenize(article_text)
            stopwords = nltk.corpus.stopwords.words('english')

            word_frequencies = {}  
            for word in nltk.word_tokenize(formatted_article_text):  
                if word not in stopwords:
                   if word not in word_frequencies.keys():
                       word_frequencies[word] = 1
                   else:
                       word_frequencies[word] += 1

            maximum_frequncy = max(word_frequencies.values())

            for word in word_frequencies.keys():  
                word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
            
            sentence_scores = {}  
            for sent in sentence_list:  
                for word in nltk.word_tokenize(sent.lower()):
                    if word in word_frequencies.keys():
                       if len(sent.split(' ')) < 30:
                          if sent not in sentence_scores.keys():
                             sentence_scores[sent] = word_frequencies[word]
                          else:
                             sentence_scores[sent] += word_frequencies[word]
            # save the results
            summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
            summary = ' '.join(summary_sentences) 
            results = summary
    return render_template('index.html', errors=errors, results=results)


if __name__ == '__main__':
    app.run(host= '0.0.0.0' )