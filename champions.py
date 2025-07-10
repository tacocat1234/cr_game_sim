from abstract_classes import Troop

class Champion(Troop):
    def __init__(self, s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, m_s, d_t, m, c_r, p, ability_cost, cloned=False):
        super().__init__(s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, m_s, d_t, m, c_r, p, cloned)
        self.ability_cost = ability_cost

    def activate_ability(self, arena):
        if self.side:
            arena.p1_elixir -= self.ability_cost
        else:
            arena.p2_elixir -= self.ability_cost