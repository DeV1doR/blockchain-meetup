pragma solidity ^0.4.15;

contract Activator {
    
    UserStorage store;
    
    struct UserStorage {
        mapping(address => bool) regUsers;
        mapping(address => string) userBox;
        uint length;
        uint limit;
    }
    
    event Error(bytes32);
    event Success(bytes32);
    
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
        if (store.regUsers[msg.sender]) {
            emit Error('User already registered');
            return false;
        }
        if (store.length >= store.limit) {
            emit Error('Store does no have left space');
            return false;
        }
        store.regUsers[msg.sender] = true;
        store.userBox[msg.sender] = note;
        store.length += 1;
        emit Success('Reg success');
        return true;
    }
    
    function unreg() public returns (bool) {
        if (!store.regUsers[msg.sender]) {
            emit Error('User not registered');
            return false;
        }
        if (store.length < 1) {
            emit Error('Store must have space');
            return false;
        }
        store.regUsers[msg.sender] = false;
        store.userBox[msg.sender] = "";
        store.length -= 1;
        emit Success('Unreg success');
        return true;
    }
}
