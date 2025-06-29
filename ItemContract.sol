// SPDX-License-Identifier: MIT
pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

contract ItemContract {
    uint256 public itemCounter;

    // 设备的信息
    struct Item {
        uint256 id;
        string name; 
        uint256 power;
        address owner;
        string equ_address;
        uint256 price; // 新添加的设备金额参数
        string addTime; // 新添加的设备添加时间参数
    }
    // 在出售列表
    uint256[] public id_list;

    mapping(uint256 => Item) public items;
    mapping(address => uint256[]) public userItems;

    event ItemCreated(uint256 id, string name, uint256 power, address owner,string equ_address,uint256 price,string addTime); // 修改事件
    event ItemTransferred(uint256 id, address from, address to);

    // 创建设备
    function createItem(
        string memory _name,
        uint256 _power,
        address _owner,
        string  _equ_local,
        uint256 _price, // 新添加的设备金额参数
        string _addTime
    ) public {
        itemCounter++;
        items[itemCounter] = Item(itemCounter, _name, _power, _owner,_equ_local,0,_addTime); //默认金额是0  
        userItems[_owner].push(itemCounter);
        emit ItemCreated(itemCounter, _name, _power, _owner,_equ_local,0,_addTime); 
    }
    // 判断一下这个是不是自己的设备，不是则没发添加(否则任何人都可以把你设备添加到出售列表)，
    // 这样同时可以防止这个item不存在的情况，也会返回 “你不是设备拥有人”
    // 在使用flask调用时，传入一个调用合约的请求人传入一个地址（配合flask中的函数传入自己登录账户的当前地址）

    // 将想出售的设备添加到出售列表中

    function addItemToSaleList(uint256 itemId, uint256 price) public {
        // 判断一下这个是不是自己的设备，不是则没发添加(否则任何人都可以把你设备添加到出售列表)
        bool isOnSale = false;
        for (uint i = 0; i < id_list.length; i++) {
            if (id_list[i] == itemId) {
                isOnSale = true;
                break;
            }
        }
        require(items[itemId].owner == msg.sender && !isOnSale, "你不是设备拥有人或该设备已在出售列表中.");
        items[itemId].price = price;
        id_list.push(itemId);
    }
    // 调用这个函数获取这个id_list列表的内容（获取正在出售的商品列表）
    function getIdList() public view returns (uint256[] memory) {
        return id_list;
    }

    // 获取全部设备id的列表 
    function getAllItems() public view returns (uint256[] memory) {
        uint256[] memory allItems = new uint256[](itemCounter);
        for (uint256 i = 1; i <= itemCounter; i++) {
            allItems[i - 1] = i;
        }
        return allItems;
    }
    // 传入地址获取用户设备列表
    function getUserItems(
        address _user
    ) public view returns (uint256[] memory) {
        return userItems[_user];
    }

    // 传入设备的编号，获取设备信息
    function getItem(uint256 itemId) public view returns (Item memory) {
        return items[itemId];
    }

    // 将设备所有权从当前所有者转移到新的地址 （如果传入的to地址和出售地址相同，就是取消出售）
    // 这里判断一下这个itemId的设备id是不是在正在出售的设备列表中，不是则没法执行下面转移的合约
    function transferItem(address to, uint256 itemId) public {
        // 判断这个设备是否在出售列表中

        bool isOnSale = false;
        uint256 index = 0;
        for (uint i = 0; i < id_list.length; i++) {
            if (id_list[i] == itemId) {
                isOnSale = true;
                index = i;
                break;
            }
        }
        require(isOnSale, "该设备不在出售列表中，无法转移.");
        address originalOwner = items[itemId].owner; // 添加此行以存储原始所有者的地址

        // 将设备所有权从当前所有者转移到新的地址
        items[itemId].owner = to;
        items[itemId].price = 0; // 将设备金额设置为0

        if (index < id_list.length) {
            // 将要删除的元素置为空
            delete id_list[index];
            // 将最后一个元素移到要删除的位置上
            id_list[index] = id_list[id_list.length - 1];
            // 将数组长度减1，即删除最后一个元素
            id_list.length--;
        }

        // 更新用户设备列表
        // uint256[] storage userItemsFrom = userItems[items[itemId].owner];
        uint256[] storage userItemsFrom = userItems[originalOwner];
        uint256[] storage userItemsTo = userItems[to];
        bool itemFound = false;
        for (uint256 j = 0; j < userItemsFrom.length; j++) {
            if (userItemsFrom[j] == itemId) {
            // 将设备从原所有者的设备列表中移除
            userItemsFrom[j] = userItemsFrom[userItemsFrom.length - 1];
            userItemsFrom.length--;
            itemFound = true;
            break;
        }
    }

    if (itemFound) {
    // 将设备添加到新的所有者的设备列表中
        userItemsTo.push(itemId);
    }
        emit ItemTransferred(itemId, originalOwner, to);
    }
    // //////////////////////////能源
    mapping(uint256 => address) public energySellers;
    mapping(uint256 => uint256) public energyPrices;
    mapping(uint256 => uint256) public energyAmounts; // 新增：存储每个能源ID的出售数量
    mapping(address => uint256) public userEnergy;
    uint256 public energyCounter;

    // 添加一个添加能源的函数
    function addEnergy(address user, uint256 amount) public {
        userEnergy[user] += amount;
    }

    // 购买能源
    function buyEnergy(uint256 energyId, uint256 amountToBuy) public payable {
        address seller = energySellers[energyId];
        uint256 price = energyPrices[energyId];
        uint256 sellerEnergy = userEnergy[seller];
        uint256 availableEnergy = energyAmounts[energyId]; // 获取当前能源ID的出售数量

        require(msg.sender != seller, "卖家不能购买自己的能源"); // 确保买家和卖家不是同一个人
        require(seller != address(0), "无效的能源ID");
        require(amountToBuy > 0 && amountToBuy <= availableEnergy, "购买数量不合理"); // 检查购买数量是否小于或等于出售数量
        userEnergy[msg.sender] += amountToBuy;
        userEnergy[seller] -= amountToBuy;
        energyAmounts[energyId] -= amountToBuy; // 修改：减少出售数量
        if (energyAmounts[energyId] == 0) {
            delete energySellers[energyId];
            delete energyPrices[energyId];
        }
    }

    // 出售能源
    function sellEnergy(uint256 amount, uint256 price) public {
        require(userEnergy[msg.sender] >= amount, "出售能量不足");

        energyCounter++;
        energySellers[energyCounter] = msg.sender;
        energyPrices[energyCounter] = price;
        energyAmounts[energyCounter] = amount; // 新增：设置出售数量
        userEnergy[msg.sender] -= amount;
    }

    // 查询能源价格
    function getEnergyPrice(uint256 energyId) public view returns (uint256) {
        return energyPrices[energyId];
    }
    //取消订单
    function cancelEnergySale(uint256 energyId) public {
        // 检查能源ID是否有效
        require(energySellers[energyId] != address(0), "无效的能源ID");
        // 检查当前用户是否是能源卖家
        require(energySellers[energyId] == msg.sender, "只有能源卖家才能取消销售");

        uint256 energyAmount = energyAmounts[energyId]; // 获取能源出售数量

        // 将能源数量退还给卖家
        userEnergy[msg.sender] += energyAmount;

        // 删除能源ID、价格和卖家信息
        delete energySellers[energyId];
        delete energyPrices[energyId];
        delete energyAmounts[energyId];
    }
    // 获取查询用户能源
    function getUserEnergy(address user) public view returns (uint256) {
        return userEnergy[user];
    }
    // 查看用户正在出售中的能源
    function getUserAvailableEnergy(address user) public view returns (uint256[] memory ids, uint256[] memory prices, uint256[] memory amounts) {
        uint256 userAvailableCount = 0;
        for (uint256 ii = 1; ii <= energyCounter; ii++) {
            if (energySellers[ii] == user) {
                userAvailableCount++;
            }
        }

        ids = new uint256[](userAvailableCount);
        prices = new uint256[](userAvailableCount);
        amounts = new uint256[](userAvailableCount);

        uint256 index = 0;
        for (uint256 jj = 1; jj <= energyCounter; jj++) {
            if (energySellers[jj] == user) {
                ids[index] = jj;
                prices[index] = energyPrices[jj];
                amounts[index] = energyAmounts[jj];
                index++;
            }
        }
    }
    // 查看正在出售中的能源
    function getAvailableEnergy() public view returns (uint256[] memory ids, address[] memory sellers, uint256[] memory prices, uint256[] memory amounts) {
        uint256 availableCount = 0;
        for (uint256 i = 1; i <= energyCounter; i++) {
            if (energySellers[i] != address(0)) {
                availableCount++;
            }
        }

        ids = new uint256[](availableCount);
        sellers = new address[](availableCount);
        prices = new uint256[](availableCount);
        amounts = new uint256[](availableCount); // 新增：存储每个能源ID的出售数量

        uint256 index = 0;
        for (uint256 j = 1; j <= energyCounter; j++) {
            if (energySellers[j] != address(0)) {
                ids[index] = j;
                sellers[index] = energySellers[j];
                prices[index] = energyPrices[j];
                amounts[index] = energyAmounts[j]; // 新增：设置每个能源ID的出售数量
                index++;
            }
        }
    }
}
