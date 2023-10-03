import React from 'react'
import {
    HiOutlineColorSwatch,
    HiOutlineDesktopComputer,
    HiOutlineTemplate,
    HiOutlineViewGridAdd,
    HiOutlineHome,
    HiUserAdd,
    HiUserGroup,
    HiOutlineUserGroup,
    HiCog
} from 'react-icons/hi'

const navigationIcon = {
    home: <HiOutlineHome />,
    //singleMenu: <HiOutlineViewGridAdd />,
    userNav: <HiUserAdd />,
    accountNav: <HiOutlineUserGroup />,
    settingNav: <HiCog />,
    collapseMenu: <HiOutlineTemplate />,
    groupSingleMenu: <HiOutlineDesktopComputer />,
    groupCollapseMenu: <HiOutlineColorSwatch />,
}

export default navigationIcon
