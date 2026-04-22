import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import json

# --- ARCHITECTURE HELPER CLASSES ---

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, kernel_size=4):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, padding="same")
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU()
        self.shortcut = nn.Conv1d(in_channels, out_channels, kernel_size=1) if in_channels != out_channels else nn.Identity()
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=(kernel_size // 2) // 2)

    def forward(self, x):
        output = self.relu(self.bn1(self.conv1(x)))
        output = output + self.shortcut(x)
        return self.conv2(output)

class DownsamplingNetwork(nn.Module):
    def __init__(self, embedding_dim=128, hidden_dim=64, in_channels=1, initial_mean_pooling_kernel_size=2, strides=[6, 6, 8, 4, 2]):
        super().__init__()
        self.mean_pooling = nn.MaxPool1d(kernel_size=initial_mean_pooling_kernel_size)
        self.layers = nn.ModuleList([ResidualBlock(hidden_dim if i > 0 else in_channels, hidden_dim, stride=strides[i], kernel_size=8) for i in range(len(strides))])
        self.final_conv = nn.Conv1d(hidden_dim, embedding_dim, kernel_size=4, padding="same")

    def forward(self, x):
        x = self.mean_pooling(x)
        for layer in self.layers: x = layer(x)
        return self.final_conv(x)

def calculate_attention(values, keys, query):
    scores = torch.matmul(query, keys.transpose(-2, -1)) / math.sqrt(keys.shape[-1])
    scores = F.softmax(scores, dim=-1)
    return torch.matmul(scores, values), scores

# --- TRANSFORMER SUB-MODULES (Fixed to match state_dict) ---

class PositionalEncoding(nn.Module):
    def __init__(self, max_seq_length, embed_size):
        super().__init__()
        self.positional_embedding = nn.Parameter(torch.zeros(max_seq_length, embed_size))

    def forward(self, x):
        return x + self.positional_embedding[:x.size(1), :]

class AttentionLayer(nn.Module):
    def __init__(self, embed_size):
        super().__init__()
        self.query_dense = nn.Linear(embed_size, embed_size)
        self.key_dense = nn.Linear(embed_size, embed_size)
        self.value_dense = nn.Linear(embed_size, embed_size)

    def forward(self, x):
        q, k, v = self.query_dense(x), self.key_dense(x), self.value_dense(x)
        attn, _ = calculate_attention(v, k, q)
        return attn

class FeedForward(nn.Module):
    def __init__(self, embed_size):
        super().__init__()
        self.layer1 = nn.Linear(embed_size, embed_size)
        self.gelu = nn.GELU()
        self.layer2 = nn.Linear(embed_size, embed_size)

    def forward(self, x):
        return self.layer2(self.gelu(self.layer1(x)))

class TransformerBlock(nn.Module):
    def __init__(self, embed_size):
        super().__init__()
        self.layer_norm1 = nn.LayerNorm(embed_size)
        self.attention_layer = AttentionLayer(embed_size)
        self.layer_norm2 = nn.LayerNorm(embed_size)
        self.feed_forward = FeedForward(embed_size)

    def forward(self, x):
        x = x + self.attention_layer(self.layer_norm1(x))
        x = x + self.feed_forward(self.layer_norm2(x))
        return x

class Transformer(nn.Module):
    def __init__(self, embed_size, num_layers, max_seq_length):
        super().__init__()
        self.positional_encoding = PositionalEncoding(max_seq_length, embed_size)
        self.transformer_blocks = nn.ModuleList([TransformerBlock(embed_size) for _ in range(num_layers)])

    def forward(self, x):
        x = self.positional_encoding(x)
        for b in self.transformer_blocks: x = b(x)
        return x

# --- QUANTIZATION CLASSES ---

class VectorQuantizer(nn.Module):
    def __init__(self, num_embeddings, embedding_dim, commitment_cost=0.25):
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings, embedding_dim)
        self.commitment_cost = commitment_cost

    def forward(self, x):
        flat_x = x.view(-1, x.shape[-1])
        dist = torch.cdist(flat_x, self.embedding.weight)
        idx = torch.argmin(dist, dim=1)
        quantized = self.embedding(idx).view(x.shape)
        loss = torch.mean((quantized - x.detach())**2) + self.commitment_cost * torch.mean((quantized.detach() - x)**2)
        return x + (quantized - x).detach(), loss

class ResidualVectorQuantizer(nn.Module):
    def __init__(self, num_codebooks, codebook_size, embedding_dim):
        super().__init__()
        self.codebooks = nn.ModuleList([VectorQuantizer(codebook_size, embedding_dim) for _ in range(num_codebooks)])

    def forward(self, x):
        out, total_loss = 0, 0
        for cb in self.codebooks:
            this_out, this_loss = cb(x)
            x, out, total_loss = x - this_out, out + this_out, total_loss + this_loss
        return out, total_loss

# --- MAIN EXPORT CLASSES ---

class Tokenizer:
    def __init__(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        tokens_list = data.get("added_tokens", [])
        self.char_map = {t["content"]: t["id"] for t in tokens_list}
        self.index_map = {t["id"]: t["content"] for t in tokens_list}
        self.vocab_size, self.blank_token = len(self.char_map), 0

    def decode(self, tokens):
        return "".join([self.index_map.get(int(t), "") for t in tokens if int(t) > 1])

class TranscribeModel(nn.Module):
    def __init__(self, num_codebooks, codebook_size, embedding_dim, vocab_size, strides, initial_mean_pooling_kernel_size, num_transformer_layers, max_seq_length=2048):
        super().__init__()
        self.options = locals(); self.options.pop('self'); self.options.pop('__class__')
        self.downsampling_network = DownsamplingNetwork(embedding_dim, embedding_dim // 2, strides=strides, initial_mean_pooling_kernel_size=initial_mean_pooling_kernel_size)
        self.pre_rvq_transformer = Transformer(embedding_dim, num_layers=num_transformer_layers, max_seq_length=max_seq_length)
        self.rvq = ResidualVectorQuantizer(num_codebooks, codebook_size, embedding_dim)
        self.output_layer = nn.Linear(embedding_dim, vocab_size)

    def forward(self, x):
        x = self.downsampling_network(x.unsqueeze(1)).transpose(1, 2)
        x, vq_loss = self.rvq(self.pre_rvq_transformer(x))
        return torch.log_softmax(self.output_layer(x), dim=-1), vq_loss

    def save(self, path):
        torch.save({"model": self.state_dict(), "options": self.options}, path)

    @staticmethod
    def load(path, device='cpu'):
        ckpt = torch.load(path, map_location=device)
        model = TranscribeModel(**ckpt["options"])
        model.load_state_dict(ckpt["model"])
        return model