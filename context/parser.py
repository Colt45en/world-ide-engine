"""
TextParser - spaCy-powered linguistic processing.
Handles tokenization, POS tagging, dependency parsing, and entity recognition.
"""

import spacy
from typing import List, Dict, Any


class TextParser:
    """Linguistic processing using spaCy."""
    
    def __init__(self, model: str = "en_core_web_sm"):
        """Initialize parser with spaCy model."""
        try:
            self.nlp = spacy.load(model)
        except OSError:
            raise RuntimeError(
                f"spaCy model '{model}' not found. "
                f"Run: python -m spacy download {model}"
            )
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse text and extract linguistic features.
        
        Returns:
            Dictionary containing:
            - tokens: List of token dictionaries
            - entities: List of named entities
            - sentences: List of sentence texts
        """
        doc = self.nlp(text)
        
        tokens = []
        for token in doc:
            tokens.append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "head": token.head.text,
                "is_stop": token.is_stop,
                "is_alpha": token.is_alpha,
            })
        
        entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]
        
        sentences = [sent.text for sent in doc.sents]
        
        return {
            "tokens": tokens,
            "entities": entities,
            "sentences": sentences,
            "text": text,
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract significant keywords from text."""
        doc = self.nlp(text)
        keywords = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha and not token.is_stop and token.pos_ in ("NOUN", "VERB", "ADJ")
        ]
        return keywords
