import {fireEvent,render,screen} from "@testing-library/react";import{vi,it,expect}from"vitest";
const auth=vi.hoisted(()=>({login:vi.fn(),register:vi.fn(),logout:vi.fn(),user:null}));
vi.mock("../context/AuthContext.jsx",()=>({useAuth:()=>auth}));
import Login from "./Login.jsx";import Register from "./Register.jsx";import{Navbar}from"../components/layout/AppShell.jsx";
it("renders login and development privacy warning",()=>{render(<Login/>);expect(screen.getByRole("heading",{name:"Log in"})).toBeInTheDocument();expect(screen.getByText(/do not enter real patient-identifiable data/i)).toBeInTheDocument();});
it("renders public registration without privileged role selection",()=>{render(<Register/>);expect(screen.getByRole("heading",{name:"Register"})).toBeInTheDocument();expect(screen.queryByText("admin")).not.toBeInTheDocument();});
it("hides therapist navigation for patient role",()=>{render(<Navbar currentPage="home" hasReport={false} onNavigate={vi.fn()} user={{role:"patient"}}/>);expect(screen.queryByRole("button",{name:"Therapist"})).not.toBeInTheDocument();});
