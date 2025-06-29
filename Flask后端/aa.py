from Flask后端.models.energy import add_user_energy_impl

data = {"address": "0x10ed86d3f921b75655f993feec18d8a94b3cd415", "amount": 100}  # amount为能源数量
response = add_user_energy_impl(data)