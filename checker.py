# import nltk
import re
from nltk.tokenize import word_tokenize
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import rabin_karp
import numpy as np
from os.path import dirname, join


class EssaiChecker:
   def __init__(self, file_a, file_b):
      self.file_a = file_a
      self.file_b = file_b
      self.hash_table = {"a": [], "b": []}
      self.k_gram = 3
      content_a = self.get_file_content(self.file_a)
      content_b = self.get_file_content(self.file_b)
      self.calculate_hash(content_a, "a")
      self.calculate_hash(content_b, "b")
       
   # menghitung nilai hash dari isi file
   # dan ditambahkan ke tabel hash tipe dokumen
   def calculate_hash(self, content, doc_type):
      text = self.preprocessing(content)
      text = "".join(text)

      print(text)

      text = rabin_karp.rolling_hash(text, self.k_gram)
      for _ in range(len(content) - self.k_gram + 1):
         self.hash_table[doc_type].append(text.hash)
         if text.next_window() == False:
            break

   def get_rate(self):
      return self.calaculate_essai_rate(self.hash_table)
   
   # kalkulasi rumus
   def calaculate_essai_rate(self, hash_table):
      th_a = len(hash_table["a"])
      th_b = len(hash_table["b"])
      a = hash_table["a"]
      b = hash_table["b"]
      sh = len(np.intersect1d(a, b))
      print(sh, a, b)

      # rumus
      # P = (2 * SH / THA * THB ) 100%
      p = (float(2 * sh)/(th_a + th_b)) * 100
      return p
   
   # mengambil/melihat isi file
   def get_file_content(self, filename):
      file = open(filename, 'r+', encoding="utf-8")
      return file.read()
   
   # preprocessing
   def preprocessing(self, content):
      # 1. case folding
      lower_case = content.lower()

      # 2. regex
      regex = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",lower_case).split())

      # 3. stopword removal
      stopword_factory = StopWordRemoverFactory().get_stop_words()
      more_stopword = ['berikut', 'www', 'world wide web']

      data = stopword_factory + more_stopword
      dictionary = ArrayDictionary(data)

      stopword = StopWordRemover(dictionary)
      hasil_stopword = stopword.remove(regex)

      # 4. stemming
      stemmer_factory = StemmerFactory()
      stemmer = stemmer_factory.create_stemmer()
      hasil_stemmer = stemmer.stem(hasil_stopword)

      # 5. tokenizing
      token = word_tokenize(hasil_stemmer)

      print(token)

      return token

current_dir = dirname(__file__)
checker = EssaiChecker(
   join(current_dir, "./pattern.txt"),
   join(current_dir, "./text.txt")
)

print('Tingkat kebenaran jawaban adalah {0}%'.format(round(checker.get_rate(), 2)))