import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const NavContainer = styled.div`
  position: fixed;
  left: 0;
  top: 0;
  width: 250px;
  height: 100vh;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 0;
  z-index: 1000;
`;

const Logo = styled.div`
  padding: 0 20px 30px;
  color: white;
  font-size: 18px;
  font-weight: 700;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const NavList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 20px 0 0 0;
`;

const NavItem = styled.li`
  margin: 5px 0;
`;

const NavLink = styled(Link)`
  display: block;
  padding: 12px 20px;
  color: ${props => props.active ? '#fff' : 'rgba(255, 255, 255, 0.8)'};
  text-decoration: none;
  font-weight: ${props => props.active ? '600' : '400'};
  background: ${props => props.active ? 'rgba(255, 255, 255, 0.1)' : 'transparent'};
  border-right: ${props => props.active ? '3px solid #00ff88' : 'none'};
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
`;

const Navigation = () => {
  const location = useLocation();

  return (
    <NavContainer>
      <Logo>QA Automation Platform</Logo>
      <NavList>
        <NavItem>
          <NavLink to="/" active={location.pathname === '/' ? 1 : 0}>
            Dashboard
          </NavLink>
        </NavItem>
        <NavItem>
          <NavLink to="/security" active={location.pathname === '/security' ? 1 : 0}>
            Security Scans
          </NavLink>
        </NavItem>
        <NavItem>
          <NavLink to="/load-testing" active={location.pathname === '/load-testing' ? 1 : 0}>
            Load Testing
          </NavLink>
        </NavItem>
        <NavItem>
          <NavLink to="/quality-gates" active={location.pathname === '/quality-gates' ? 1 : 0}>
            Quality Gates
          </NavLink>
        </NavItem>
      </NavList>
    </NavContainer>
  );
};

export default Navigation;
