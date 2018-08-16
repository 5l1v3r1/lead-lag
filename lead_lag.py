import numpy as np

from cpython_contrast import CrossCorrelationHY


def overlap(min1, max1, min2, max2):
    return max(0, min(max1, max2) - max(min1, min2))


def shifted_modified_hy_estimator(x, y, t_x, t_y, k, normalize=False):  # contrast function
    hy_cov = 0.0
    if normalize:
        norm_x = 0.0
        for ii in zip(t_x, t_x[1:]):
            norm_x += (x[ii[1]] - x[ii[0]]) ** 2
        norm_x = np.sqrt(norm_x)
        norm_y = 0.0
        for jj in zip(t_y, t_y[1:]):
            norm_y += (y[jj[1]] - y[jj[0]]) ** 2
        norm_y = np.sqrt(norm_y)
    else:
        norm_x = 1.0
        norm_y = 1.0
    for ii in zip(t_x, t_x[1:]):
        for jj in zip(t_y, t_y[1:]):
            increments_mul = (x[ii[1]] - x[ii[0]]) * (y[jj[1]] - y[jj[0]])
            overlap_term = overlap(ii[0], ii[1], jj[0] - k, jj[1] - k) > 0.0
            hy_cov += increments_mul * overlap_term
    hy_cov /= (norm_x * norm_y)
    return np.abs(hy_cov)


def run():
    # ===== DATA PART =====
    use_synthetic_data = True

    if use_synthetic_data:
        print('Using synthetic data (Bachelier).')
        from scripts.read_bachelier_data import bachelier_data
        x, y, t_x, t_y, lead_lag = bachelier_data()
    else:
        print('Using bitcoin data.')
        from scripts.read_bitcoin_data import bitcoin_data
        x, y, t_x, t_y = bitcoin_data()
        # in that case we don't know the lead lag so we can just set a big value here.
        lead_lag = 20
    # ===== DATA PART =====

    # ===== TEST PART =====
    print('Starting test phase...')
    test_lag_range = [-20, 40, 0, 10, 50, 32, 31, 83]
    contrasts_1 = CrossCorrelationHY(x, y, t_x, t_y, test_lag_range, normalize=True).fast_inference()
    contrasts_2 = CrossCorrelationHY(x, y, t_x, t_y, test_lag_range, normalize=True).slow_inference()
    np.testing.assert_almost_equal(contrasts_1, contrasts_2)
    print('Test phase completed [success]...')
    # ===== TEST PART =====

    # ===== COMPUTATION ====
    gn_max = lead_lag * 2
    print('Now computing the contrasts... The complexity is O(N^2). So be (very) patient..')
    lag_range = np.arange(-gn_max, gn_max, 1)
    contrasts = CrossCorrelationHY(x, y, t_x, t_y, lag_range, normalize=True).fast_inference()

    import matplotlib.pyplot as plt
    plt.title('Contrast = f(Lag)')
    plt.ylabel('Contrast')
    plt.xlabel('Lag')
    plt.scatter(range(len(contrasts)), contrasts, s=10)
    plt.show()

    # could have a better granularity.
    est_lead_lag_index = np.argmax(contrasts)
    print('Est. lead lag =', lag_range[est_lead_lag_index])
    # ===== COMPUTATION ====


if __name__ == '__main__':
    run()
