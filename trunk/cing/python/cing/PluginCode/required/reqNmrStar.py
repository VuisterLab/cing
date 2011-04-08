NMRSTAR_STR       = "NmrStar"

tagNameListSsaHeader = """
            Triplet_count
            Swap_count
            Swap_percentage
            Deassign_count
            Deassign_percentage
            Model_count
            Total_e_low_states
            Total_e_high_states
            Crit_abs_e_diff
            Crit_rel_e_diff
            Crit_mdls_favor_pct
            Crit_sing_mdl_viol
            Crit_multi_mdl_viol
            Crit_multi_mdl_pct
""".split()

tagNameDescriptionListSsaHeader = [
    "Number of triplets (atom-group pair and pseudo)",
    "Number of triplets that were swapped",
    "Percentage of triplets that were swapped",
    "Number of deassigned triplets",
    "Percentage of deassigned triplets",
    "Number of models in ensemble",
    "Energy of the states with the lower energies summed for all triplets (Ang.**2) ensemble averaged",
    "Energy of the states with the higher energies summed for all triplets (Ang.**2) ensemble averaged",
    "Criterium for swapping assignment on the absolute energy difference (Ang.**2)",
    "Criterium for swapping assignment on the relative energy difference (Ang.**2)",
    "Criterium for swapping assignment on the percentage of models favoring a swap",
    "Criterium for deassignment on a single model violation (Ang.)",
    "Criterium for deassignment on a multiple model violation (Ang.)",
    "Criterium for deassignment on a percentage of models"
]
