# Attribution for the speaker diarization models

The model files in this folder are **not** our work. They are redistributed
unchanged under the terms of the Creative Commons Attribution 4.0
International licence (CC BY 4.0), whose full text is in
`LICENSE-CC-BY-4.0.txt`.

## What this is

    Title    speaker-diarization-community-1
    Authors  pyannoteAI, and Hervé Bredin
    Origin   https://hf.co/pyannote/speaker-diarization-community-1
    Licence  CC BY 4.0  --  https://creativecommons.org/licenses/by/4.0/
    Revision 3533c8cf8e369892e6b79ff1bf80f7b0286a54ee

The model card as published by the authors is kept alongside as
`MODEL_CARD.md`; it was read from the official repository itself, not from
a copy. The file names, sizes and SHA-256 checksums are listed in
`SHA256SUMS.txt`, together with the second revision the same bytes carry in
the authors' ungated mirror.

## What is in the folder

    config.yaml                      the pipeline description
    segmentation/pytorch_model.bin   the speaker segmentation model
    embedding/pytorch_model.bin      the speaker embedding model
    plda/plda.npz                    the clustering model
    plda/xvec_transform.npz          the clustering model

Five files, 32 821 421 bytes together. The folder is laid out the way the
authors published it, so `Pipeline.from_pretrained('<this folder>')` reads
it directly -- no cache, no environment variable, no network.

## Not modified

**The files are passed on exactly as they were published.** Nothing was
retrained, quantised, converted, renamed or repacked. Every byte of every
file matches the upstream revision named above; the checksums in
`SHA256SUMS.txt` are the proof.

## Works to cite

The authors ask that these three papers are cited when the pipeline is
used. They are reproduced here as they stand in the model card.

1. Speaker segmentation model

```bibtex
@inproceedings{Plaquet23,
  author={Alexis Plaquet and Hervé Bredin},
  title={{Powerset multi-class cross entropy loss for neural speaker diarization}},
  year=2023,
  booktitle={Proc. INTERSPEECH 2023},
}
```

2. Speaker embedding model

```bibtex
@inproceedings{Wang2023,
  title={Wespeaker: A research and production oriented speaker embedding learning toolkit},
  author={Wang, Hongji and Liang, Chengdong and Wang, Shuai and Chen, Zhengyang and Zhang, Binbin and Xiang, Xu and Deng, Yanlei and Qian, Yanmin},
  booktitle={ICASSP 2023, IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={1--5},
  year={2023},
  organization={IEEE}
}
```

3. Speaker clustering

```bibtex
@article{Landini2022,
  author={Landini, Federico and Profant, J{\'a}n and Diez, Mireia and Burget, Luk{\'a}{\v{s}}},
  title={{Bayesian HMM clustering of x-vector sequences (VBx) in speaker diarization: theory, implementation and analysis on standard tasks}},
  year={2022},
  journal={Computer Speech \& Language},
}
```

The authors also name their own acknowledgment, which is carried over:
training and tuning were made possible by GENCI on the Jean Zay
supercomputer.

## What this notice does not claim

Redistributing the files is what CC BY 4.0 allows and what this notice
accounts for. It does not make this copy an official one. The official
place to get the models is the repository named under **Origin**; it asks
for a free account and a read token, and that route stays the recommended
one.
