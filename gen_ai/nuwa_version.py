import torch
from nuwa_pytorch import NUWAVideoAudio, VQGanVAE

# autoencoder

vae = VQGanVAE(
    dim = 64,
    num_layers = 4,
    image_size = 256,
    num_conv_blocks = 2,
    vq_codebook_size = 100
)

# NUWA transformer

nuwa = NUWAVideoAudio(
    vae = vae,
    dim = 512,
    num_audio_tokens = 2048,                # codebook size for audio tokens
    num_audio_tokens_per_video_frame = 32,  # number of audio tokens per video frame
    cross_modality_attn_every = 3,          # cross modality attention every N layers
    text_num_tokens = 20000,                # number of text tokens
    text_enc_depth = 1,                     # text encoder depth
    text_enc_heads = 8,                     # number of attention heads for encoder
    text_max_seq_len = 256,                 # max sequence length of text conditioning tokens (keep at 256 as in paper, or shorter, if your text is not that long)
    max_video_frames = 10,                  # number of video frames
    image_size = 256,                       # size of each frame of video
    dec_depth = 4,                          # video decoder depth
    dec_heads = 8,                          # number of attention heads in decoder
    enc_reversible = True,                  # reversible encoders, if you need it
    dec_reversible = True,                  # quad-branched reversible network, for making depth of twin video / audio decoder independent of network depth. recommended to be turned on unless you have a ton of memory at your disposal
    attn_dropout = 0.05,                    # dropout for attention
    ff_dropout = 0.05,                      # dropout for feedforward
    sparse_3dna_kernel_size = (5, 3, 3),    # kernel size of the sparse 3dna attention. can be a single value for frame, height, width, or different values (to simulate axial attention, etc)
    sparse_3dna_dilation = (1, 2, 4),       # cycle dilation of 3d conv attention in decoder, for more range
    shift_video_tokens = True               # cheap relative positions for sparse 3dna transformer, by shifting along spatial dimensions by one
).cuda()

# data

text = torch.randint(0, 20000, (1, 256)).cuda()
audio = torch.randint(0, 2048, (1, 32 * 10)).cuda() # (batch, audio tokens per frame * max video frames)
video = torch.randn(1, 10, 3, 256, 256).cuda() # (batch, frames, channels, height, width)

# loss = nuwa(
#     text = text,
#     video = video,
#     audio = audio,
#     return_loss = False  # set this to True, only for training, to return cross entropy loss
# )

# loss.backward()

# do above with as much data as possible

# then you can generate a video from text

video, audio = nuwa.generate(text = text, num_frames = 5) # (1, 5, 3, 256, 256), (1, 32 * 5 == 160)