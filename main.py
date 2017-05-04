from data_provider import *
from structure_processor import *
from evaluation import *
from model import *
from plotting import *
import numpy as np
from keras.callbacks import LearningRateScheduler


def main():
    train_set, test_set, params = open_dataset()
    # kfold_cv_eval(
    #     lambda: get_model(params["max_ag_len"], params["max_cdr_len"]),
    #     combine_datasets(train_set, test_set))
    # return

    max_ag_len = params["max_ag_len"]
    max_cdr_len = params["max_cdr_len"]
    max_ag_atoms = params["max_ag_atoms"]
    max_cdr_atoms = params["max_cdr_atoms"]
    max_atoms_per_residue = params["max_atoms_per_residue"]
    # pos_class_weight = params["pos_class_weight"]

    # print("Max AG length:", max_ag_len)
    # print("Max CDR length:", max_cdr_len)
    # print("Pos class weight:", pos_class_weight)

    model = get_model(max_ag_atoms, max_cdr_atoms,
                      max_atoms_per_residue, max_cdr_len)
    print(model.summary())

    ags_atoms_train, cdr_atoms_train, lbls_train, mask_train = train_set
    ags_atoms_test, cdr_atoms_test, lbls_test, mask_test = test_set
    example_weight = np.squeeze((lbls_train * 1.7 + 1) * mask_train)

    rate_schedule = lambda e: 0.001

    history = model.fit([ags_atoms_train, cdr_atoms_train,
                         np.squeeze(mask_train)],
                        lbls_train, batch_size=32,
                        epochs=40, validation_split=0.15,
                        sample_weight=example_weight,
                        callbacks=[LearningRateScheduler(rate_schedule)])

    model.save_weights("current.h5")
    probs_test = model.predict([ags_atoms_test, cdr_atoms_test, mask_test])

    test_seq_lens = np.sum(np.squeeze(mask_test), axis=1)
    probs_flat = flatten_with_lengths(probs_test, test_seq_lens)
    lbls_flat = flatten_with_lengths(lbls_test, test_seq_lens)

    pos_idx = probs_test > 0.5
    pred_test = np.zeros_like(probs_test)
    pred_test[pos_idx] = 1
    pred_flat = flatten_with_lengths(pred_test, test_seq_lens)

    print(confusion_matrix(lbls_flat, pred_flat))

    #plot_roc_curve(lbls_flat, probs_flat)
    #plot_prec_rec_curve(lbls_flat, probs_flat,
    #                    output_filename="abip-sets.pdf")

    # plot_stats(history)
    # annotate_and_save_test_structures(probs_test)

if __name__ == "__main__":
    main()