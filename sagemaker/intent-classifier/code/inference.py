import os
import json
from dataclasses import dataclass, asdict
import traceback
from loguru import logger
import numpy as np
import torch
from torch import nn
from transformers import BertModel, AutoTokenizer
from kobert_tokenizer import KoBERTTokenizer

@dataclass
class PredictionOutput:
    intent: str
    confidence: float

JSON_CONTENT_TYPE = "application/json"

class BERTClassifier(nn.Module):
    def __init__(self,
                 bert,
                 hidden_size=768,
                 num_classes=6,
                 dr_rate=None,
                 params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate
        self.softmax = nn.Softmax(dim=-1)
        self.classifier = nn.Linear(hidden_size, num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def forward(self, token_ids, attention_mask, segment_ids):
        _, pooler = self.bert(
            input_ids=token_ids,
            token_type_ids=segment_ids.long(),
            attention_mask=attention_mask.float().to(token_ids.device),
            return_dict=False
        )
        if self.dr_rate:
            out = self.dropout(pooler)
        out = self.classifier(out)
        out = self.softmax(out)
        idx = out.cpu().detach().argmax().item()
        prob = out.cpu().detach().max().item() * 100
        return idx, prob

def model_fn(model_dir:str):
    model_name = "intent_model_1.0.0.pt"
    model_config = os.path.join(model_dir, "model", model_name)
    device = torch.device("cpu")
    bertmodel = BertModel.from_pretrained('skt/kobert-base-v1')
    tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
    model = BERTClassifier(bertmodel, dr_rate=0.5).to(device)
    model.load_state_dict(torch.load(
            model_config,
            device
    ), strict=False)
    model.eval()
    return {"model":model, "tokenizer":tokenizer}

def input_fn(serialized_input_data, content_type=JSON_CONTENT_TYPE):
    if content_type == JSON_CONTENT_TYPE:
        input_data = json.loads(serialized_input_data)
        return input_data
    else:
        raise Exception("Requested unsupported ContentType in Accept: " + content_type)
        return

def predict_fn(input_data, model_dict:dict):
    logger.info(f"Got input Data: {input_data}")
    req_text = input_data['reqSentence']
    model = model_dict['model']
    tokenizer = model_dict['tokenizer']
    device = torch.device("cpu")
    max_len=100
    try:
        category = ['일반', '추천', '정보', '건강', '공격', '와들']
        tokenized = tokenizer(
            [req_text],
            return_tensors='pt',
            padding='max_length',
            max_length=max_len
        )
        
        idx, prob = model(
            tokenized['input_ids'].to(device),
            tokenized['attention_mask'].to(device),
            tokenized['token_type_ids'].to(device)
        )
        
        intent_result = category[idx]
        confidence = prob
        return PredictionOutput(intent=intent_result, confidence=confidence)
    except Exception as e:
        logger.error("[GenerateIntent]")
        logger.debug(traceback.format_exc())
        return PredictionOutput(intent="일반", confidence=1)

def output_fn(prediction_output, accept=JSON_CONTENT_TYPE):
    if accept == JSON_CONTENT_TYPE:
        return json.dumps(asdict(prediction_output)), accept
    else:
        raise Exception("Requested unsupported ContentType in Accept: " + accept)
        return