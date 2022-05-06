"""Implements self supervised semantic shift functions
It uses poisoning attacks to learn landmarks in a self-supervised way
At each iteration, generate perturbation on the data, generating positive
and negative samples
Learn the separation between them (using any classifier)
Apply the classifier to the original (non-perturbated) data
Negatives -> landmarks
Positives -> semantically changed
We can begin by aligning on all words, and then learn better landmarks from
there. Alternatively, one can start from random landmarks."""


# Third party modules
from ast import Global
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, log_loss
from scipy.spatial.distance import cosine, euclidean
import matplotlib.pyplot as plt
import seaborn as sns

# Local modules
from ...WordVectors import WordVectors
from .global_align import GlobalAlignConfig

# Initialize random seeds
np.random.seed(1)
tf.random.set_seed(1)


class S4AlignConfig:
    def __init__(self,
    cls_model="nn",
    iters=100,
    n_targets=10,
    n_negatives=10,
    fast=True,
    rate=0,
    t=0.5,
    t_overlap=1,
    landmarks=None,
    update_landmarks=True
):
        self.cls_model = cls_model
        self.iters = int(iters)
        self.n_targets = int(n_targets)
        self.n_negatives = int(n_negatives)
        self.fast = int(fast)
        self.rate = float(rate)
        self.t = float(t)
        self.t_overlap = float(t_overlap)
        self.landmarks = landmarks
        self.update_landmarks = update_landmarks

    def align(self, wv1, wv2):
        """
        aligns wv1 to wv2 using orthogonal procrustes with anchors chosen by s4
        """
        landmarks, non_landmarks, Q = s4(wv1, wv2, cls_model=self.cls_model,
                                         iters=self.iters, n_targets=self.n_targets,
                                         n_negatives=self.n_negatives, fast=self.fast,
                                         rate=self.rate, t=self.t, t_overlap=self.t_overlap,
                                         landmarks=self.landmarks,
                                         update_landmarks=self.update_landmarks)
        _wv1vec = np.matmul(wv1.vectors, Q)
        _wv1 = WordVectors(wv1.get_words(), _wv1vec)
        return _wv1, wv2, Q


def negative_samples(words, size, p=None):
    """
    Returns negative samples of semantic change
    May use distribution of cosine distance as sampling distribution
    """
    neg_samples = np.random.choice(words, size, p=p)
    return neg_samples


def inject_change_single(wv, w, words, v_a, alpha, replace=False, max_tries=50):
    """
    Injects change to word w in wv by randomly selecting a word t in wv
    and injecting the sense of t in to w.
    The modified vector of w must have a higher cosine distance to v_a
    than its original version. This is done by sampling t while the cosine of
    w is not greater than that of v_a and wv(w) or until a max_tries.
    v_a is the vector of word w in the parallel corpus (not wv).

    Arguments:
            wv      -   WordVectors of the corpus to be modified
            w       -   (str) Word to be modified
            words   -   (list) Pool of words to sample from, injecting sense
            v_a     -   (np.ndarray) word vector of w in the source parallel to wv
            alpha   -   (float) Rate of injected change
            replace -   (bool) Whether to replace w with t instead of 'moving' w towards t
    Returns:
            x       -   (np.ndarray) modified vector of w
    """
    cos_t = cosine(
        v_a, wv.get_vector(w)
    )  # cosine distance threshold we want to surpass
    c = 0
    tries = 0
    v_b = np.copy(wv.get_vector(w))
    while c < cos_t and tries < max_tries:
        tries += 1
        selected = np.random.choice(words)  # select word with new sense
        if not replace:
            b = wv.get_vector(w) + alpha * wv.get_vector(selected)
            v_b = b
        else:
            v_b = wv.get_vector(selected)
        c = cosine(v_a, v_b)
    return v_b


def get_features(x, names=["cos"]):
    """
    Compute features given input training data (concatenated vectors)
    Default features is cosine. Accepted features: cosine (cos).
    Attributes:
            x   - size n input training data as concatenated word vectors
            names - size d list of features to compute
    Returns:
            n x d feature matrix (floats)
    """
    x_out = np.zeros((len(x), len(names)), dtype=float)
    for i, p in enumerate(x):
        for j, feat in enumerate(names):
            if feat == "cos":
                x_ = cosine(p[: len(p) // 2], p[len(p) // 2 :])
                x_out[i][j] = x_
    return x_out


def build_sklearn_model():
    """
    Build SVM using sklearn model
    The model uses an RBF kernel and the features are given by difference
    between input vectors u-v.
    Return: sklearn SVC
    """
    model = SVC(random_state=0, probability=True)
    return model


def build_keras_model(dim):
    """
    Builds the keras model to be used in self-supervision.
    Return: Keras-Tensorflow2 model
    """
    h1_dim = 100
    h2_dim = 100
    model = keras.Sequential(
        [
            keras.layers.Input(shape=(dim)),
            keras.layers.Dense(
                h1_dim,
                activation="relu",
                activity_regularizer=keras.regularizers.l2(1e-2),
            ),
            # keras.layers.Dense(h2_dim, activation="relu",
            #                    activity_regularizer=keras.regularizers.l2(1e-2)),
            keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(optimizer="rmsprop", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def threshold_crossvalidation(
    wv1,
    wv2,
    iters=100,
    n_fold=1,
    n_targets=100,
    n_negatives=100,
    fast=True,
    rate=0.5,
    t=0.5,
    landmarks=None,
    t_overlap=1,
    debug=False,
):
    """
    Runs crossvalidation over self-supervised samples, carrying out a model
    selection to determine the best cosine threshold to use in the final
    prediction.

    Arguments:
        wv1, wv2    - input WordVectors - required to be intersected and ALIGNED before call
        plot        - 1: plot functions in the end 0: do not plot
        iters       - max no. of iterations
        n_fold      - n-fold crossvalidation (1 - leave one out, 10 - 10-fold cv, etc.)
        n_targets   - number of positive samples to generate
        n_negatives - number of negative samples
        fast        - use fast semantic change simulation
        rate        - rate of semantic change injection
        t           - classificaiton threshold (0.5)
        t_overlap   - overlap threshold for (stop criterion)
        landmarks   - list of words to use as landmarks (classification only)
        debug       - toggles debugging mode on/off. Provides reports on several metrics. Slower.
    Returns:
        t - selected cosine threshold t
    """

    wv2_original = WordVectors(words=wv2.words, vectors=wv2.vectors.copy())
    landmark_set = set(landmarks)
    non_landmarks = [w for w in wv1.words if w not in landmark_set]

    for iter in range(iters):

        replace = dict()  # replacement dictionary
        pos_samples = list()
        pos_vectors = dict()

        # Randomly sample words to inject change to
        # If no word is flagged as non_landmarks, sample from all words
        # In practice, this should never occur when selecting landmarks
        # but only for classification when aligning on all words
        if len(non_landmarks) > 0:
            targets = np.random.choice(non_landmarks, n_targets)
            # Make targets deterministic
            # targets = non_landmarks
        else:
            targets = np.random.choice(wv1.words, n_targets)

        for target in targets:

            # Simulate semantic change in target word
            v = inject_change_single(wv2_original, target, wv1.words, wv1[target], rate)

            pos_vectors[target] = v

            pos_samples.append(target)
        # Convert to numpy array
        pos_samples = np.array(pos_samples)
        # Get negative samples from landmarks
        # when p is none, we sample from all words
        neg_samples = negative_samples(landmarks, n_negatives, p=None)
        neg_vectors = {w: wv2_original[w] for w in neg_samples}
        # Create dictionary of supervision samples (positive and negative)
        # Mapping word -> vector
        sup_vectors = {**neg_vectors, **pos_vectors}

        # Prepare training data
        words_train = np.concatenate((pos_samples, neg_samples))
        # assign labels to positive and negative samples
        y_train = [1] * len(pos_samples) + [0] * len(neg_samples)

        # Stack columns to shuffle data and labels together
        train = np.column_stack((words_train, y_train))
        # Shuffle batch
        np.random.shuffle(train)
        # Detach data and labels
        words_train = train[:, 0]
        y_train = train[:, -1].astype(int)

        # Calculate cosine distance of training samples
        x_train = np.array([cosine(wv1[w], sup_vectors[w]) for w in words_train])

        # t_pool = [0.2, 0.7]
        t_pool = np.arange(0.2, 1, 0.1)

        best_acc = 0
        best_t = 0
        for t_ in t_pool:
            acc = 0
            for i in range(0, len(x_train), n_fold):
                x_cv = x_train[i : i + n_fold]
                y_true = y_train[i : i + n_fold]
                y_hat = x_cv > t_
                acc += sum(y_hat == y_true) / len(x_cv)
            acc = acc / (len(x_train) // n_fold)
            if acc > best_acc:
                best_acc = acc
                best_t = t_
                print("- New best t", t_, acc)

    return best_t


def s4(
    wv1,
    wv2,
    verbose=0,
    plot=0,
    cls_model="nn",
    iters=100,
    n_targets=10,
    n_negatives=10,
    fast=True,
    rate=0,
    t=0.5,
    t_overlap=1,
    landmarks=None,
    update_landmarks=True,
    return_model=False,
    debug=False,
):
    """
    Performs self-supervised learning of semantic change.
    Generates negative samples by sampling from landmarks.
    Generates positive samples via simulation of semantic change on random non-landmark words.
    Trains a classifier, fine-tune it across multiple iterations.
    If update_landmarks is True, then it learns landmarks from that step. In this case,
    the returned values are landmarks, non_landmarks, Q (transform matrix)
    Otherwise, landmarks are fixed from a starting set and the returned value
    is the learned classifier - landmarks must be passed.
    Arguments:
        wv1, wv2    - input WordVectors - required to be intersected before call
        verbose     - 1: display log, 0: quiet
        plot        - 1: plot functions in the end 0: do not plot
        cls_model   - classification model to use {"nn", "svm_auto", "svm_features"}
        iters       - max no. of iterations
        n_targets   - number of positive samples to generate
        n_negatives - number of negative samples
        fast        - use fast semantic change simulation
        rate        - rate of semantic change injection
        t           - classificaiton threshold (0.5)
        t_overlap   - overlap threshold for (stop criterion)
        landmarks   - list of words to use as landmarks (classification only)
        update_landmarks - if True, learns landmarks. Otherwise, learns classification model.
        debug       - toggles debugging mode on/off. Provides reports on several metrics. Slower.
    Returns:
        if update_landmarks is True:
            landmarks - list of landmark words
            non_landmarks - list of non_landmark words
            Q           - transformation matrix for procrustes alignment
        if update_landmarks is False:
            model       - binary classifier
    """

    # Define verbose prints
    if verbose == 1:

        def verbose_print(*s, end="\n"):
            print(*s, end=end)

    elif verbose == 0:

        def verbose_print(*s, end="\n"):
            return None

    wv2_original = WordVectors(words=wv2.get_words(), vectors=wv2.vectors.copy())

    avg_window = 0  # number of iterations to use in running average

    ga = GlobalAlignConfig()
    # Begin alignment
    if update_landmarks:
        # Check if landmarks is initialized
        if landmarks == None:
            wv1, wv2, Q = ga.align(wv1, wv2)  # start from global alignment
            landmark_dists = [euclidean(u, v) for u, v in zip(wv1.vectors, wv2.vectors)]
            landmark_args = np.argsort(landmark_dists)
            landmarks = [
                wv1.get_words()[i]
                for i in landmark_args[: int(len(wv1.get_words()) * 0.5)]
            ]
            # landmarks = np.random.choice(wv1.words, int(len(wv1)*0.5))
        landmark_set = set(landmarks)
        non_landmarks = np.array([w for w in wv1.get_words() if w not in landmark_set])
    else:
        landmark_set = set(landmarks)
        non_landmarks = [w for w in wv1.get_words() if w not in landmark_set]
    # modify the global alignment config to use the landmarks we found

    ga.anchor_words = landmarks
    # align
    wv1, wv2, Q = ga.align(wv1, wv2)
    if cls_model == "nn":
        print("dim is", wv1.get_vector_dimension())
        model = build_keras_model(wv1.get_vector_dimension() * 2)
    elif cls_model == "svm_auto" or cls_model == "svm_features":
        model = build_sklearn_model()  # get SVC

    landmark_hist = list()  # store no. of landmark history
    loss_hist = list()  # store self-supervision loss history
    alignment_loss_hist = list()  # store landmark alignment loss
    alignment_out_hist = list()  # store alignment loss outside of lm
    alignment_all_hist = list()

    cumulative_out_hist = list()
    cumulative_alignment_hist = list()  # store cumulative loss alignment
    overlap_hist = list()  # store landmark overlap history
    cumulative_overlap_hist = list()  # mean overlap history
    cumulative_loss = 0

    # History of cosines
    cos_loss_in_hist = list()
    cos_loss_out_hist = list()
    cumulative_cos_in = list()
    cumulative_cos_out = list()

    prev_landmarks = set(landmarks)
    for iter in range(iters):

        pos_samples = list()
        pos_vectors = dict()

        # Randomly sample words to inject change to
        # If no word is flagged as non_landmarks, sample from all words
        # In practice, this should never occur when selecting landmarks
        # but only for classification when aligning on all words
        if len(non_landmarks) > 0:
            targets = np.random.choice(non_landmarks, n_targets)
            # Make targets deterministic
            # targets = non_landmarks
        else:
            targets = np.random.choice(wv1.words, n_targets)

        for target in targets:

            # Simulate semantic change in target word
            v = inject_change_single(
                wv2_original, target, wv1.get_words(), wv1[target], rate
            )

            pos_vectors[target] = v

            pos_samples.append(target)
        # Convert to numpy array
        pos_samples = np.array(pos_samples)
        # Get negative samples from landmarks
        neg_samples = negative_samples(landmarks, n_negatives, p=None)
        neg_vectors = {w: wv2_original[w] for w in neg_samples}
        # Create dictionary of supervision samples (positive and negative)
        # Mapping word -> vector
        sup_vectors = {**neg_vectors, **pos_vectors}

        # Prepare training data
        words_train = np.concatenate((pos_samples, neg_samples))
        # assign labels to positive and negative samples
        y_train = [1] * len(pos_samples) + [0] * len(neg_samples)

        # Stack columns to shuffle data and labels together
        train = np.column_stack((words_train, y_train))
        # Shuffle batch
        np.random.shuffle(train)
        # Detach data and labels
        words_train = train[:, 0]
        y_train = train[:, -1].astype(int)

        x_train = np.array([np.append(wv1[w], sup_vectors[w]) for w in words_train])

        # Append history
        landmark_hist.append(len(landmarks))
        v1_land = np.array([wv1[w] for w in landmarks])
        v2_land = np.array([wv2_original[w] for w in landmarks])
        v1_out = np.array([wv1[w] for w in non_landmarks])
        v2_out = np.array([wv2_original[w] for w in non_landmarks])

        alignment_loss = np.linalg.norm(v1_land - v2_land) ** 2 / len(v1_land)
        alignment_loss_hist.append(alignment_loss)
        cumulative_alignment_hist.append(np.mean(alignment_loss_hist[-avg_window:]))

        # out loss
        alignment_out_loss = np.linalg.norm(v1_out - v2_out) ** 2 / len(v1_out)
        alignment_out_hist.append(alignment_out_loss)
        cumulative_out_hist.append(np.mean(alignment_out_hist[-avg_window:]))

        # all loss
        alignment_all_loss = np.linalg.norm(
            wv1.vectors - wv2_original.vectors
        ) ** 2 / len(wv1.words)
        alignment_all_hist.append(alignment_all_loss)

        if debug:
            # cosine loss
            cos_in = np.mean([cosine(u, v) for u, v in zip(v1_land, v2_land)])
            cos_out = np.mean([cosine(u, v) for u, v in zip(v1_out, v2_out)])
            cos_loss_in_hist.append(cos_in)
            cos_loss_out_hist.append(cos_out)
            cumulative_cos_in.append(np.mean(cos_loss_in_hist))
            cumulative_cos_out.append(np.mean(cos_loss_out_hist))

        # Begin training of neural network
        if cls_model == "nn":
            print("training")
            print("dset size:", len(x_train))
            history = model.train_on_batch(x_train, y_train, reset_metrics=False)
            # history = model.fit(x_train, y_train, epochs=5, verbose=0)
            # history = [history.history["loss"][0]]
        elif cls_model == "svm_auto":
            model.fit(x_train, y_train)
            pred_train = model.predict_proba(x_train)
            history = [log_loss(y_train, pred_train)]
        elif cls_model == "svm_features":
            x_train_ = get_features(x_train)  # retrieve manual features
            model.fit(x_train_, y_train)
            pred_train = model.predict_proba(x_train_)
            y_hat_t = pred_train[:, 0] > 0.5
            acc_t = accuracy_score(y_train, y_hat_t)
            history = [log_loss(y_train, pred_train), acc_t]

        loss_hist.append(history[0])

        # Apply model on original data to select landmarks
        x_real = np.array(
            [np.append(u, v) for u, v in zip(wv1.vectors, wv2_original.vectors)]
        )
        if cls_model == "nn":
            predict_real = model.predict(x_real)
        elif cls_model == "svm_auto":
            predict_real = model.predict_proba(x_real)
            predict_real = predict_real[:, 1]
        elif cls_model == "svm_features":
            x_real_ = get_features(x_real)
            predict_real = model.predict_proba(x_real_)
            predict_real = predict_real[:, 1]

        y_predict = predict_real > t

        if update_landmarks:
            landmarks = [
                wv1.get_word(i) for i in range(len(wv1.words)) if predict_real[i] < t
            ]
            non_landmarks = [
                wv1.get_word(i) for i in range(len(wv1.words)) if predict_real[i] > t
            ]

        # Update landmark overlap using Jaccard Index
        isect_ab = set.intersection(prev_landmarks, set(landmarks))
        union_ab = set.union(prev_landmarks, set(landmarks))
        j_index = len(isect_ab) / len(union_ab)
        overlap_hist.append(j_index)

        cumulative_overlap_hist.append(
            np.mean(overlap_hist[-avg_window:])
        )  # store mean

        prev_landmarks = set(landmarks)

        verbose_print(
            "> %3d | L %4d | l(in): %.2f | l(out): %.2f | loss: %.2f | overlap %.2f | acc: %.2f"
            % (
                iter,
                len(landmarks),
                cumulative_alignment_hist[-1],
                cumulative_out_hist[-1],
                history[0],
                cumulative_overlap_hist[-1],
                history[1],
            ),
            end="\r",
        )
        ga.landmarks = landmarks
        wv1, wv2_original, Q = ga.align(wv1, wv2_original)

        # Check if overlap difference is below threhsold
        if np.mean(overlap_hist) > t_overlap:
            break

    # Print new line
    verbose_print()

    if plot == 1:
        iter += 1  # add one to iter for plotting
        plt.plot(range(iter), landmark_hist, label="landmarks")
        plt.hlines(len(wv1.words), 0, iter, colors="red")
        plt.ylabel("No. of landmarks")
        plt.xlabel("Iteration")
        plt.show()
        plt.plot(range(iter), loss_hist, c="red", label="loss")
        plt.ylabel("Loss (binary crossentropy)")
        plt.xlabel("Iteration")
        plt.legend()
        plt.show()
        plt.plot(range(iter), cumulative_alignment_hist, label="in (landmarks)")
        plt.plot(range(iter), cumulative_out_hist, label="out")
        plt.plot(range(iter), alignment_all_hist, label="all")
        plt.ylabel("Alignment loss (MSE)")
        plt.xlabel("Iteration")
        plt.legend()
        plt.show()

        if debug:
            plt.plot(range(iter), cumulative_cos_in, label="cos in")
            plt.plot(range(iter), cumulative_cos_out, label="cos out")
            plt.legend()
            plt.show()

        plt.plot(range(iter), cumulative_overlap_hist, label="overlap")

        plt.ylabel("Jaccard Index", fontsize=16)
        plt.xlabel("Iteration", fontsize=16)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        # plt.legend()
        plt.tight_layout()
        plt.savefig("overlap.pdf", format="pdf")
        # plt.show()

    if update_landmarks:
        if not return_model:
            return landmarks, non_landmarks, Q
        else:
            return landmarks, non_landmarks, Q, model
    else:
        return model
