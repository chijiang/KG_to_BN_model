import {
    HomeOutlined,
    AreaChartOutlined,
    BuildOutlined,
    DatabaseOutlined,
    SettingOutlined
} from '@ant-design/icons';

const menuList = [
    {
        label: "首页",
        key: "/bowayKng/home",
        icon: <HomeOutlined style={{ color: "white" }} />,
    },
    {
        label: "选项1",
        icon: <AreaChartOutlined style={{ color: "white" }} />,
        key: "/bowayKng/opt1"
    },
    {
        label: "选项2",
        icon: <BuildOutlined style={{ color: "white" }} />,
        key: "/bowayKng/opt2"
    },
    {
        label: "知识图谱金字塔",
        icon: <DatabaseOutlined style={{ color: "white" }} />,
        key: "/bowayKng/kg_graph",
        children: [
            {
                label: "制造通用知识",
                key: "/bowayKng/kg_graph/generalKn",
            },
            {
                label: "金属工业知识",
                key: "/bowayKng/kg_graph/metalKn",
            },
            {
                label: "博威铜合金业务知识",
                key: "/bowayKng/kg_graph/bowayKn",
            }
        ]
    },
    {
        label: "AI专家",
        icon: <DatabaseOutlined style={{ color: "white" }} />,
        key: "/bowayKng/aiExpert",
        children: [
            {
                label: "质量问题分析",
                key: "/bowayKng/aiExpert/qualities",
            },
            {
                label: "TBD",
                key: "/bowayKng/aiExpert/__tbd",
            }
        ]
    },
    {
        label: "系统设置",
        icon: <SettingOutlined style={{ color: "white" }} />,
        key: "/bowayKng/system_settings",
        children: [
            {
                label: "系统变量",
                key: "/bowayKng/system_settings/system_variables"
            },
            {
                label: "人员管理",
                key: "/bowayKng/system_settings/user_management"
            }
        ]
    }
]

export default menuList;