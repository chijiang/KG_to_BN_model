import React, { useState } from 'react';
import axios from 'axios';
import { Select, Button, Row, Col, Input } from 'antd';

const QualityFailurePage = () => {
  const [selectedOption, setSelectedOption] = useState('');
  const [response, setResponse] = useState('');

  const handleOptionChange = (e) => {
    setSelectedOption(e.target.value);
  };

  const handleQuery = () => {
    let data = JSON.stringify({
      "target": selectedOption
    });
    let config = {
      method: 'post',
      maxBodyLength: Infinity,
      url: '/bayesian_net',
      headers: {
        'Content-Type': 'application/json'
      },
      data: data
    };

    // Calling bayesian network api
    axios.request(config)
      .then((response) => {
        setResponse(JSON.stringify(response.data));
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <div>
      <h1>质量失效查询</h1>
      <Row>
        <Col span={24}>
          <span>
            <Select placeholder={"请选择炉型"}>
              <option value="铜镍硅B型炉">铜镍硅B型炉</option>
            </Select>
          </span>
          <span>
            <Select placeholder={"请选择牌号"}>
              <option value="C70250">C70250</option>
            </Select>
          </span>
        </Col>
      </Row>

      <Select
        placeholder={"请选择失效问题"}
        value={selectedOption}
        onChange={handleOptionChange}
        style={{ width: "240px" }}>
        <option value="冷隔">冷隔</option>
        <option value="气孔">气孔</option>
        <option value="夹渣">夹渣</option>
        <option value="铸锭/铸坯开裂">铸锭/铸坯开裂</option>
        <option value="熔铸起皮">熔铸起皮</option>
        <option value="气泡">气泡</option>
        <option value="孔洞">孔洞</option>
        <option value="裂纹">裂纹</option>
      </Select>
      <Button onClick={handleQuery}>查询</Button>
      <h3>概率查询</h3>
      <div>
        <Input value={response} readOnly style={{ width: '50%', minHeight: '400px', resize: 'none' }} />
      </div>
    </div>
  );
};

export default QualityFailurePage;
