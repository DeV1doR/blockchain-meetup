pragma solidity ^0.4.15;

contract Activator {
    
    UserStorage store;
    
    struct UserStorage {
        mapping(address => bool) regUsers;
        mapping(address => string) userBox;
        uint length;
        uint limit;
    }
    
    function Activator(uint _limit) public {
        store = UserStorage({limit: _limit, length: 0});
    }
    
    function userExist() public view returns (bool) {
        return store.regUsers[msg.sender];
    }
    
    function getNote() public view returns (string) {
        return store.userBox[msg.sender];
    }
    
    function reg(string note) public returns (bool) {
        require(!store.regUsers[msg.sender]);
        require(store.length < store.limit);
        store.regUsers[msg.sender] = true;
        store.userBox[msg.sender] = note;
        store.length += 1;
        return true;
    }
    
    function unreg() public returns (bool) {
        require(store.regUsers[msg.sender]);
        require(store.length >= 0);
        store.regUsers[msg.sender] = false;
        store.userBox[msg.sender] = "";
        store.length -= 1;
        return true;
    }
}
