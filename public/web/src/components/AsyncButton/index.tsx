import { Button, ButtonProps } from "antd";
import { useState } from "react";
interface IProps extends Omit<ButtonProps, 'onClick'> {
    onClick?: () => Promise<any>
}
const AsyncButton: React.FC<IProps> = props => {
    const { onClick, loading } = props;
    const [btnLoading, setLoading] = useState<boolean>(false)

    const onHandleClick = async () => {
        setLoading(true)
        try {
            await onClick?.()
        } finally {
            setLoading(false)
        }
    }

    return <Button {...props} onClick={onHandleClick} loading={loading || btnLoading} />
}

export default AsyncButton;