import torch


def attention_score(att, x_lens, mel_lens, r=1):
    att, x_lens, mel_lens = att.detach()[:], x_lens.detach()[:], mel_lens.detach()[:]
    device = att.device
    b, t_max, c_max = att.size()

    # create mel padding mask
    mel_range = torch.arange(0, t_max, device=device)
    mel_lens = mel_lens // r
    mask = (mel_range[None, :] < mel_lens[:, None]).float()

    # score for how adjacent the attention loc is
    max_loc = torch.argmax(att, dim=2)
    max_loc_diff = torch.abs(max_loc[:, 1:] - max_loc[:, :-1])
    loc_score = (max_loc_diff >= 0) * (max_loc_diff <= r)
    loc_score = torch.sum(loc_score * mask[:, 1:], dim=1)
    loc_score = loc_score / (mel_lens - 1)

    # score for attention sharpness
    sharp_score, inds = att.max(dim=2)
    sharp_score = torch.mean(sharp_score, dim=1)

    return loc_score, sharp_score